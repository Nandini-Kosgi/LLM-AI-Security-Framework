import argparse, json, statistics, os
from typing import List, Dict

def compute_metrics(rows: List[Dict]):
    benign = [r for r in rows if r["category"] == "benign" and r.get("status") == "ok"]
    attacks = [r for r in rows if r["category"] != "benign" and r.get("status") == "ok"]
    latencies = [r.get("latency_ms",0) for r in rows if r.get("status") == "ok"]

    # Attack Success Rate: attack allowed
    asr_numer = sum(1 for r in attacks if r.get("allowed", True) is True)
    asr_denom = max(1, len(attacks))
    asr = asr_numer / asr_denom

    # Detection Rate: attack blocked (inverse of ASR)
    dr = 1.0 - asr

    # False Positive Rate: benign blocked
    fpr_numer = sum(1 for r in benign if r.get("allowed", True) is False)
    fpr_denom = max(1, len(benign))
    fpr = fpr_numer / fpr_denom

    p50 = statistics.median(latencies) if latencies else 0
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies) if latencies else 0

    return {
        "count_total": len(rows),
        "count_attacks": len(attacks),
        "count_benign": len(benign),
        "ASR": round(asr, 3),
        "DR": round(dr, 3),
        "FPR": round(fpr, 3),
        "latency_p50_ms": int(p50),
        "latency_p95_ms": int(p95),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--infile", default="reports/run.json")
    p.add_argument("--outfile", default="reports/summary.json")
    args = p.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        rows = json.load(f)
    metrics = compute_metrics(rows)

    os.makedirs("reports", exist_ok=True)
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
