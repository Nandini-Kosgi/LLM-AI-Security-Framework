import argparse, time, json, os
from typing import Dict, List
import httpx, yaml
from tqdm import tqdm

def load_cases(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    out = []
    for cat in data.get("categories", []):
        for c in cat.get("cases", []):
            out.append({"category": cat["name"], "prompt": c})
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:8000")
    p.add_argument("--prompts", default="redteam/prompts.yaml")
    p.add_argument("--outfile", default="reports/run.json")
    args = p.parse_args()

    cases = load_cases(args.prompts)
    results = []
    with httpx.Client(timeout=60) as client:
        for case in tqdm(cases, desc="Running red-team"):
            t0 = time.time()
            try:
                r = client.post(f"{args.base_url}/chat", json={"user_input": case["prompt"]})
                latency_ms = int((time.time() - t0) * 1000)
                if r.status_code == 200:
                    data = r.json()
                    meta = data.get("meta", {})
                    results.append({
                        **case,
                        "status": "ok",
                        "latency_ms": latency_ms,
                        "allowed": meta.get("allowed", True),
                        "pre_hits": meta.get("pre_hits", []),
                        "post_hits": meta.get("post_hits", []),
                        "output": data.get("output", ""),
                    })
                else:
                    results.append({**case, "status": f"http_{r.status_code}"})
            except Exception as e:
                results.append({**case, "status": f"error:{e}"})

    os.makedirs("reports", exist_ok=True)
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved: {args.outfile} ({len(results)} cases)")

if __name__ == "__main__":
    main()
