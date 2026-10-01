"""Train the email triage classifier on emails that a person already sorted.

Each subfolder of Sorted is a category; each .txt file in it is one email (a subject line, an empty line, the body).
The script asks the local embedding model (Ollama) for one vector per email, trains a logistic regression on the
vectors, measures its accuracy by cross-validation, calibrates its confidence and writes triage-model.json.
The language model is not changed: only a small table of weights is learnt, in seconds, on the CPU.

Usage:  python train_triage.py [--sorted Sorted] [--embedding-model embeddinggemma] [--out triage-model.json]
Needs:  Ollama with the embedding model (ollama pull embeddinggemma), Python 3.10+, numpy and scikit-learn.
"""
import argparse
import datetime
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

OLLAMA = "http://127.0.0.1:11434/api/embed"  # 127.0.0.1, not localhost: Ollama listens on IPv4 and localhost tries IPv6 first (2 s lost per call)


def embed(model, texts):
    body = json.dumps({"model": model, "input": texts}).encode("utf-8")
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        vectors = np.array(json.loads(resp.read().decode("utf-8"))["embeddings"], dtype=np.float64)
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sorted", default="Sorted", help="folder with one subfolder per category")
    ap.add_argument("--embedding-model", default="embeddinggemma")
    ap.add_argument("--out", default="triage-model.json")
    a = ap.parse_args()

    root = Path(a.sorted)
    files = sorted(p for p in root.glob("*/*.txt"))
    labels = [p.parent.name for p in files]
    classes = sorted(set(labels))
    counts = {c: labels.count(c) for c in classes}
    if len(classes) < 2 or min(counts.values()) < 2:
        sys.exit(f"Need at least 2 categories with 2 emails each in {root.resolve()}; found {counts}")
    print(f"{len(files)} emails in {len(classes)} categories: {counts}")

    t0 = time.perf_counter()
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in files]
    x = np.vstack([embed(a.embedding_model, texts[i:i + 16]) for i in range(0, len(texts), 16)])
    y = np.array([classes.index(l) for l in labels])
    print(f"embedded in {time.perf_counter() - t0:.1f} s with {a.embedding_model}")

    # Out-of-fold scores: every email is scored by a model that never saw it
    folds = min(5, min(counts.values()))
    logits = np.zeros((len(y), len(classes)))
    for train, test in StratifiedKFold(n_splits=folds, shuffle=True, random_state=0).split(x, y):
        m = LogisticRegression(C=10, max_iter=3000).fit(x[train], y[train])
        logits[np.ix_(test, m.classes_)] = m.decision_function(x[test])
    # Temperature: the one value that makes the confidence honest on those out-of-fold scores
    temps = np.exp(np.linspace(np.log(0.05), np.log(5), 200))
    nll = [-np.log(softmax(logits / t)[np.arange(len(y)), y] + 1e-12).mean() for t in temps]
    temperature = float(temps[int(np.argmin(nll))])
    proba = softmax(logits / temperature)
    pred, conf = proba.argmax(axis=1), proba.max(axis=1)
    accuracy = float((pred == y).mean())
    sure = conf >= 0.8
    print(f"cross-validated accuracy: {accuracy:.1%}; confidence >= 80 %: {sure.mean():.0%} of the emails, "
          f"{(pred[sure] == y[sure]).mean():.1%} of them right")

    final = LogisticRegression(C=10, max_iter=3000).fit(x, y)
    model = {"embedding_model": a.embedding_model, "classes": classes, "temperature": temperature,
             "coef": final.coef_.round(6).tolist(), "intercept": final.intercept_.round(6).tolist(),
             "trained_on": len(files), "cv_accuracy": round(accuracy, 4),
             "created": datetime.date.today().isoformat()}
    Path(a.out).write_text(json.dumps(model), encoding="utf-8")
    print(f"model written to {Path(a.out).resolve()}")


if __name__ == "__main__":
    main()
