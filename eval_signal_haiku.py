"""
Eval: signal_extractor on Opus 4.7 vs Haiku 4.5.

Replays historical (utterance, directive) pairs from logs/sessions/ through
both models and compares outputs along the dimensions that matter for
routing _extract_signal to Haiku.
"""

import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic
from dotenv import load_dotenv
load_dotenv(override=True)

from llm_session import _prompt, _parse_json, _validate_signal

OPUS = "claude-opus-4-7"
HAIKU = "claude-haiku-4-5"
LOGS_DIR = Path("logs/sessions")
OUT_PATH = Path("logs/eval_signal_haiku.jsonl")

PRICING = {  # $/1M tokens
    OPUS:  {"in": 5.00, "out": 25.00},
    HAIKU: {"in": 1.00, "out":  5.00},
}


def load_historical_signals() -> list[dict]:
    """Reconstruct (utterance, directive_at_extraction_time, reference_signal)."""
    samples = []
    for log in sorted(LOGS_DIR.glob("*.jsonl")):
        current_directive = None
        with log.open() as f:
            for line in f:
                entry = json.loads(line)
                etype = entry.get("type")
                if etype == "session_open":
                    current_directive = entry["directive"]
                elif etype == "signal":
                    samples.append({
                        "source": log.name,
                        "utterance": entry["utterance"],
                        "directive": current_directive,
                        "reference_signal": entry["signal"],
                    })
                elif etype == "turn" and "directive" in entry:
                    current_directive = entry["directive"]
    return samples


def extract_signal(client, model: str, utterance: str, directive: dict) -> dict:
    """One signal extraction. Mirrors _call_with_repair's two-attempt loop."""
    system = _prompt("signal_extractor")
    user_text = (
        f"Current directive:\n{json.dumps(directive, ensure_ascii=False, indent=2)}\n\n"
        f"Student says: \"{utterance}\""
    )
    msgs = [{"role": "user", "content": user_text}]

    in_toks = out_toks = 0
    repaired = False
    t0 = time.time()

    for attempt in range(2):
        resp = client.messages.create(
            model=model, max_tokens=512, system=system, messages=msgs,
        )
        in_toks += resp.usage.input_tokens
        out_toks += resp.usage.output_tokens
        raw = resp.content[0].text

        try:
            obj = _parse_json(raw)
            errs = _validate_signal(obj)
            if not errs:
                return {
                    "ok": True, "signal": obj, "raw": raw,
                    "input_tokens": in_toks, "output_tokens": out_toks,
                    "latency_s": time.time() - t0, "repaired": repaired,
                }
            if attempt == 0:
                repaired = True
                msgs += [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content":
                        f"The JSON is missing required fields: {errs}. "
                        "Return the corrected JSON only."},
                ]
            else:
                return {"ok": False, "reason": f"schema: {errs}", "raw": raw,
                        "input_tokens": in_toks, "output_tokens": out_toks,
                        "latency_s": time.time() - t0, "repaired": repaired}
        except json.JSONDecodeError:
            if attempt == 0:
                repaired = True
                msgs += [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content":
                        "Your previous response was not valid JSON. "
                        "Return only the JSON object."},
                ]
            else:
                return {"ok": False, "reason": "json_decode", "raw": raw,
                        "input_tokens": in_toks, "output_tokens": out_toks,
                        "latency_s": time.time() - t0, "repaired": repaired}

    return {"ok": False, "reason": "unreachable"}


def run_sample(client, idx: int, sample: dict) -> dict:
    opus = extract_signal(client, OPUS, sample["utterance"], sample["directive"])
    haiku = extract_signal(client, HAIKU, sample["utterance"], sample["directive"])
    return {
        "idx": idx,
        "source": sample["source"],
        "utterance": sample["utterance"],
        "reference_signal": sample["reference_signal"],
        "opus": opus,
        "haiku": haiku,
    }


def cost(in_toks: int, out_toks: int, model: str) -> float:
    p = PRICING[model]
    return in_toks * p["in"] / 1e6 + out_toks * p["out"] / 1e6


def error_marker_types(sig: dict) -> set:
    return {m.get("type") for m in (sig.get("error_markers") or [])}


def summarize(results: list[dict]) -> None:
    n = len(results)
    print(f"\n{'='*60}\nEVAL SUMMARY — {n} samples\n{'='*60}\n")

    for label, key in [("Opus 4.7", "opus"), ("Haiku 4.5", "haiku")]:
        ok = [r for r in results if r[key]["ok"]]
        in_t = sum(r[key]["input_tokens"] for r in results)
        out_t = sum(r[key]["output_tokens"] for r in results)
        lat = [r[key]["latency_s"] for r in results]
        repaired = sum(1 for r in results if r[key].get("repaired"))
        c = cost(in_t, out_t, OPUS if key == "opus" else HAIKU)
        print(f"{label}:")
        print(f"  parse+schema ok: {len(ok)}/{n} ({100*len(ok)/n:.0f}%)")
        print(f"  needed JSON repair: {repaired}/{n}")
        print(f"  total tokens: {in_t:,} in / {out_t:,} out")
        print(f"  total cost:   ${c:.4f}")
        print(f"  latency (s):  median={statistics.median(lat):.2f}  "
              f"p95={sorted(lat)[int(0.95*n)]:.2f}")
        print()

    # Agreement (only on samples where both succeeded)
    both_ok = [r for r in results if r["opus"]["ok"] and r["haiku"]["ok"]]
    print(f"Agreement metrics (n={len(both_ok)} samples where both parsed):\n")

    # error_markers — type set agreement
    exact = 0
    partial = 0  # any overlap
    opus_zero = 0
    haiku_zero = 0
    opus_only = haiku_only = 0
    for r in both_ok:
        o = error_marker_types(r["opus"]["signal"])
        h = error_marker_types(r["haiku"]["signal"])
        if not o:
            opus_zero += 1
        if not h:
            haiku_zero += 1
        if o == h:
            exact += 1
        if o & h:
            partial += 1
        if o and not h:
            opus_only += 1
        if h and not o:
            haiku_only += 1
    print(f"  error_markers type set:")
    print(f"    exact match:     {exact}/{len(both_ok)} ({100*exact/len(both_ok):.0f}%)")
    print(f"    any overlap:     {partial}/{len(both_ok)}")
    print(f"    Opus empty:      {opus_zero}     Haiku empty: {haiku_zero}")
    print(f"    Opus-only flag:  {opus_only}     Haiku-only flag: {haiku_only}")

    # confidence distribution on error_markers
    def confs(key):
        out = []
        for r in both_ok:
            for m in (r[key]["signal"].get("error_markers") or []):
                if m.get("confidence"):
                    out.append(m["confidence"])
        return out
    from collections import Counter
    print(f"\n  confidence distribution:")
    print(f"    Opus:  {dict(Counter(confs('opus')))}")
    print(f"    Haiku: {dict(Counter(confs('haiku')))}")

    # resistance.present agreement
    res_agree = sum(
        1 for r in both_ok
        if r["opus"]["signal"].get("resistance", {}).get("present")
           == r["haiku"]["signal"].get("resistance", {}).get("present")
    )
    opus_res = sum(1 for r in both_ok if r["opus"]["signal"].get("resistance", {}).get("present"))
    haiku_res = sum(1 for r in both_ok if r["haiku"]["signal"].get("resistance", {}).get("present"))
    print(f"\n  resistance.present:")
    print(f"    agreement: {res_agree}/{len(both_ok)} ({100*res_agree/len(both_ok):.0f}%)")
    print(f"    Opus says present:  {opus_res}     Haiku says present: {haiku_res}")

    # statement_type agreement
    type_agree = sum(
        1 for r in both_ok
        if r["opus"]["signal"].get("student_statement_type")
           == r["haiku"]["signal"].get("student_statement_type")
    )
    print(f"\n  student_statement_type agreement: {type_agree}/{len(both_ok)} "
          f"({100*type_agree/len(both_ok):.0f}%)")

    # adhikara_apparent agreement
    adh_agree = sum(
        1 for r in both_ok
        if r["opus"]["signal"].get("register", {}).get("adhikara_apparent")
           == r["haiku"]["signal"].get("register", {}).get("adhikara_apparent")
    )
    print(f"  register.adhikara_apparent agreement: {adh_agree}/{len(both_ok)}")

    # per-session cost extrapolation: assume 25 signal calls/session
    opus_per = cost(
        sum(r["opus"]["input_tokens"] for r in results) / n,
        sum(r["opus"]["output_tokens"] for r in results) / n,
        OPUS,
    )
    haiku_per = cost(
        sum(r["haiku"]["input_tokens"] for r in results) / n,
        sum(r["haiku"]["output_tokens"] for r in results) / n,
        HAIKU,
    )
    print(f"\nExtrapolated cost per 25-turn session (signal extraction only):")
    print(f"  Opus 4.7:  ${opus_per * 25:.3f}")
    print(f"  Haiku 4.5: ${haiku_per * 25:.3f}")
    print(f"  Savings:   ${(opus_per - haiku_per) * 25:.3f} "
          f"({100*(opus_per - haiku_per)/opus_per:.0f}%)")


def main() -> None:
    samples = load_historical_signals()
    print(f"Loaded {len(samples)} historical signals from {LOGS_DIR}/")
    print(f"Calling {OPUS} and {HAIKU} for each → {2 * len(samples)} API calls\n")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    results: list[dict] = []

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as out:
        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = {
                ex.submit(run_sample, client, i, s): i
                for i, s in enumerate(samples)
            }
            for fut in as_completed(futures):
                r = fut.result()
                results.append(r)
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
                out.flush()
                opus_ok = "✓" if r["opus"]["ok"] else "✗"
                haiku_ok = "✓" if r["haiku"]["ok"] else "✗"
                print(f"  [{len(results):3d}/{len(samples)}] "
                      f"opus={opus_ok} haiku={haiku_ok}  "
                      f"{r['utterance'][:50]!r}")

    results.sort(key=lambda r: r["idx"])
    summarize(results)
    print(f"\nFull results: {OUT_PATH}")


if __name__ == "__main__":
    main()
