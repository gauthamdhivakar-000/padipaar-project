"""Risk scoring: weights -> 0-100 score and Low / Medium / High band."""

WEIGHTS = {
    "data_sharing": 20, "auto_renewal": 15, "hidden_fees": 15, "permissions_collection": 12,
    "liability_limit": 10, "unilateral_change": 10, "penalty_cancellation": 10,
    "arbitration_waiver": 8,
}
UI_WEIGHTS = {"pre_ticked_consent": 8, "urgency_pressure": 5, "hidden_decline": 5}
UI_BONUS_CAP = 15


def band_for(score: int) -> str:
    return "Low" if score <= 20 else "Medium" if score <= 50 else "High"


def compute_score(findings, ui_findings=None):
    """findings: list of dicts with category/confidence. ui_findings: list of {type,...}."""
    best = {}
    for f in findings:
        cat = f["category"]
        if cat in WEIGHTS:
            best[cat] = max(best.get(cat, 0.0), float(f["confidence"]))
    doc_score = sum(WEIGHTS[c] * conf for c, conf in best.items())

    ui_types = {u.get("type") for u in (ui_findings or []) if isinstance(u, dict)}
    ui_bonus = min(UI_BONUS_CAP, sum(UI_WEIGHTS.get(t, 0) for t in ui_types))

    score = int(round(min(100, doc_score + ui_bonus)))
    return {
        "score": score,
        "band": band_for(score),
        "doc_score": int(round(doc_score)),
        "ui_bonus": int(ui_bonus),
        "by_category": {c: round(v, 3) for c, v in sorted(best.items(), key=lambda kv: -kv[1])},
    }
