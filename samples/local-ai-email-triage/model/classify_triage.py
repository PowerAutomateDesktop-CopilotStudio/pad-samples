"""Classify one email with the model written by train_triage.py.

Prints one line of JSON: {"category": "invoice", "confidence_pct": 93}  (or {"error": "..."} with exit code 1).
The confidence is a whole number of percent, so that any regional setting reads it.

Usage:  python classify_triage.py --model triage-model.json --file email.txt
Needs:  Python 3.10+ and Ollama with the embedding model named in triage-model.json. No package to install.
"""
import argparse
import json
import math
import sys
import urllib.request

OLLAMA = "http://127.0.0.1:11434/api/embed"  # 127.0.0.1, not localhost: Ollama listens on IPv4 and localhost tries IPv6 first (2 s lost per call)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--file", required=True)
    a = ap.parse_args()
    try:
        with open(a.model, encoding="utf-8") as fh:
            model = json.load(fh)
        with open(a.file, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        body = json.dumps({"model": model["embedding_model"], "input": [text]}).encode("utf-8")
        req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            v = json.loads(resp.read().decode("utf-8"))["embeddings"][0]
    except Exception as exc:  # one clear line for the flow, never a stack trace
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}))
        sys.exit(1)
    norm = math.sqrt(sum(x * x for x in v))
    v = [x / norm for x in v]
    scores = [sum(w * x for w, x in zip(row, v)) + b for row, b in zip(model["coef"], model["intercept"])]
    top = max(scores)
    exp = [math.exp((s - top) / model["temperature"]) for s in scores]
    best = max(range(len(exp)), key=exp.__getitem__)
    print(json.dumps({"category": model["classes"][best], "confidence_pct": round(100 * exp[best] / sum(exp))}))


if __name__ == "__main__":
    main()
