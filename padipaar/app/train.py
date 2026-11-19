"""Train the TF-IDF + Logistic Regression multi-label classifier.

Run:  python -m app.train
"""
import json
import os

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import KFold
from sklearn.multiclass import OneVsRestClassifier

from .rules import CATEGORIES
from .training_data import POSITIVE, SAFE

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE, "models", "baseline.joblib")
METRICS_PATH = os.path.join(BASE, "models", "metrics.json")


def build_dataset():
    texts, rows = [], []
    for cat, sents in POSITIVE.items():
        for s in sents:
            texts.append(s)
            rows.append([1 if c == cat else 0 for c in CATEGORIES])
    for s in SAFE:
        texts.append(s)
        rows.append([0] * len(CATEGORIES))
    return texts, np.array(rows)


def _make_models():
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True, lowercase=True)
    clf = OneVsRestClassifier(LogisticRegression(max_iter=2000, class_weight="balanced", C=4.0))
    return vec, clf


def train_model(save=True):
    texts, Y = build_dataset()
    texts = np.array(texts, dtype=object)

    # 5-fold cross-validation on the seed set -> out-of-fold probabilities -> thresholds + metrics
    oof = np.zeros(Y.shape, dtype=float)
    for tr, te in KFold(n_splits=5, shuffle=True, random_state=42).split(texts):
        vec, clf = _make_models()
        clf.fit(vec.fit_transform(texts[tr]), Y[tr])
        oof[te] = clf.predict_proba(vec.transform(texts[te]))

    thresholds, per_cat = {}, {}
    for i, cat in enumerate(CATEGORIES):
        best_t, best_f = 0.5, -1.0
        for t in np.arange(0.35, 0.80, 0.05):
            f = f1_score(Y[:, i], oof[:, i] >= t, zero_division=0)
            if f > best_f:
                best_t, best_f = float(round(t, 2)), f
        thresholds[cat] = best_t
        pred = oof[:, i] >= best_t
        per_cat[cat] = {
            "precision": round(float(precision_score(Y[:, i], pred, zero_division=0)), 3),
            "recall": round(float(recall_score(Y[:, i], pred, zero_division=0)), 3),
            "f1": round(float(f1_score(Y[:, i], pred, zero_division=0)), 3),
            "support": int(Y[:, i].sum()),
        }
    macro_f1 = round(float(np.mean([v["f1"] for v in per_cat.values()])), 3)

    vec, clf = _make_models()
    clf.fit(vec.fit_transform(texts), Y)
    bundle = {"vec": vec, "clf": clf, "categories": CATEGORIES, "thresholds": thresholds}
    metrics = {
        "method": "5-fold cross-validation on the built-in seed set",
        "samples": int(len(texts)),
        "macro_f1": macro_f1,
        "per_category": per_cat,
        "thresholds": thresholds,
        "caveat": "Seed set is small and hand-written, so these numbers are optimistic. "
                  "Add real labelled clauses and re-run `python -m app.train` for honest metrics.",
    }
    if save:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(bundle, MODEL_PATH)
        with open(METRICS_PATH, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2)
    return bundle, metrics


if __name__ == "__main__":
    _, m = train_model(save=True)
    print("Model saved to", MODEL_PATH)
    print("Macro F1 (seed cross-validation):", m["macro_f1"])
    for c, v in m["per_category"].items():
        print("  %-24s P=%.2f R=%.2f F1=%.2f (n=%d)" % (c, v["precision"], v["recall"], v["f1"], v["support"]))
