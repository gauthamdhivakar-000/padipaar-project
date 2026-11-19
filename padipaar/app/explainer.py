"""Tamil + English explanations for findings."""
import json
import os
import re

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "explanations_ta.json")
with open(_PATH, encoding="utf-8") as _fh:
    EXPL = json.load(_fh)

_DETAIL = re.compile(
    r"(?:Rs\.?\s?[\d,]+(?:\.\d+)?|INR\s?[\d,]+(?:\.\d+)?|\u20b9\s?[\d,]+(?:\.\d+)?|\d+\s?(?:days?|months?|years?|hours?))",
    re.I,
)


def explain_finding(finding, clause):
    e = EXPL["categories"][finding["category"]]
    details = []
    for m in _DETAIL.finditer(clause):
        d = m.group(0).strip()
        if d not in details:
            details.append(d)
    return {
        "category": finding["category"],
        "confidence": finding["confidence"],
        "source": finding["source"],
        "title_en": e["title_en"], "title_ta": e["title_ta"],
        "meaning_en": e["meaning_en"], "meaning_ta": e["meaning_ta"],
        "tip_en": e["tip_en"], "tip_ta": e["tip_ta"],
        "clause": clause,
        "highlights": finding.get("highlights", []),
        "details": details[:3],
    }


def explain_ui(ui):
    """Explain one UI finding sent by the browser extension."""
    t = ui.get("type")
    e = EXPL["ui_patterns"].get(t)
    if not e:
        return None
    return {
        "type": t,
        "title_en": e["title_en"], "title_ta": e["title_ta"],
        "meaning_en": e["meaning_en"], "meaning_ta": e["meaning_ta"],
        "tip_en": e["tip_en"], "tip_ta": e["tip_ta"],
        "text": str(ui.get("text", ""))[:160],
    }


def band_summary(band):
    b = EXPL["bands"][band]
    return {"summary_en": b["summary_en"], "summary_ta": b["summary_ta"]}


def disclaimer():
    return {"en": EXPL["disclaimer_en"], "ta": EXPL["disclaimer_ta"]}
