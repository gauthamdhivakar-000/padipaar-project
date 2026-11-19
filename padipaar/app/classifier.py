"""Hybrid detector: regex rules + ML classifier, merged per category."""
import json
import os
import threading

import joblib

from .rules import CATEGORIES, NEGATION_SENSITIVE, is_negated, rule_scan
from .train import METRICS_PATH, MODEL_PATH, train_model

_lock = threading.Lock()
_bundle = None


def _load():
    global _bundle
    if _bundle is not None:
        return _bundle
    with _lock:
        if _bundle is not None:
            return _bundle
        bundle = None
        if os.path.exists(MODEL_PATH):
            try:
                bundle = joblib.load(MODEL_PATH)
            except Exception:
                bundle = None  # incompatible/corrupt file -> retrain below
        if bundle is None:
            bundle, _ = train_model(save=True)
        _bundle = bundle
    return _bundle


def model_info():
    _load()
    try:
        with open(METRICS_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"note": "metrics not available"}


def ml_scan_batch(clauses):
    """Return one list of ML findings per clause."""
    if not clauses:
        return []
    b = _load()
    probs = b["clf"].predict_proba(b["vec"].transform(clauses))
    out = []
    for clause, row in zip(clauses, probs):
        negated = is_negated(clause)
        hits = []
        for cat, p in zip(b["categories"], row):
            if p < b["thresholds"][cat]:
                continue
            if negated and cat in NEGATION_SENSITIVE:
                continue
            hits.append({"category": cat, "confidence": round(float(p), 3), "source": "ml",
                         "highlights": []})
        out.append(hits)
    return out


def analyse_clauses(clauses):
    """Return a list (one entry per clause) of merged findings."""
    ml_all = ml_scan_batch(clauses)
    results = []
    for clause, ml_hits in zip(clauses, ml_all):
        merged = {}
        for f in rule_scan(clause):
            merged[f["category"]] = dict(f)
        for f in ml_hits:
            cur = merged.get(f["category"])
            if cur is None:
                merged[f["category"]] = dict(f)
            else:  # detected by both: boost confidence a little
                cur["source"] = "both"
                cur["confidence"] = round(min(0.99, max(cur["confidence"], f["confidence"]) + 0.05), 3)
        results.append(sorted(merged.values(), key=lambda x: -x["confidence"]))
    return results


def analyse_clause(clause):
    return analyse_clauses([clause])[0]
