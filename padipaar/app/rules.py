"""Fast, explainable regex rule engine (with a negation guard)."""
import re

CATEGORIES = [
    "auto_renewal", "hidden_fees", "data_sharing", "permissions_collection",
    "liability_limit", "arbitration_waiver", "unilateral_change", "penalty_cancellation",
]

RULES = {
    "auto_renewal": [
        r"automatic(?:ally)? renew", r"auto-?renew", r"recurring (?:charge|billing|payment|subscription)",
        r"until you cancel", r"renews? (?:each|every) ", r"will be charged .{0,40}(?:each|every|until)",
    ],
    "hidden_fees": [
        r"fees? (?:may|will|can) apply", r"additional (?:charges|fees|costs)", r"processing fees?",
        r"convenience fees?", r"(?:change|revise|modify|increase) (?:our |the )?(?:prices?|pricing|fees|rates)",
        r"fees? (?:are|is) (?:not )?(?:included|refundable)",
    ],
    "data_sharing": [
        r"(?:share|disclose|provide|transfer)s? (?:your|personal|user|such)[^.]{0,80}(?:third[- ]part|partners?|affiliates?|advertis|subsidiar)",
        r"(?:sell|rent|trade|license) (?:your|personal|user)", r"share[^.]{0,40}with (?:our )?(?:marketing|advertising) ",
    ],
    "permissions_collection": [
        r"access (?:to )?(?:your )?(?:contacts|contact list|sms|text messages|messages|camera|microphone|call logs?|photos|gallery)",
        r"collect[^.]{0,60}(?:precise |exact |real-time )?(?:location|contacts|call logs?|sms|device identifiers?|biometric)",
        r"(?:read|upload|sync) your (?:contacts|messages|sms|call history)",
    ],
    "liability_limit": [
        r"(?:shall|will|are|is) not (?:be )?liable", r"no liability", r"\bas[- ]is\b", r"disclaims?[^.]{0,40}warrant",
        r"limit(?:ation)? of liability", r"in no event[^.]{0,60}liable", r"at your own risk",
    ],
    "arbitration_waiver": [
        r"binding arbitration", r"waive[^.]{0,60}(?:class action|jury|right to (?:sue|go to court))",
        r"exclusive jurisdiction", r"resolved (?:exclusively )?(?:by|through|in) arbitration",
    ],
    "unilateral_change": [
        r"(?:modify|change|update|amend|revise)[^.]{0,60}(?:at any time|without (?:prior |any )?notice|sole discretion)",
        r"sole discretion", r"terminate[^.]{0,60}(?:without (?:prior )?notice|at any time|for any reason)",
        r"suspend[^.]{0,40}(?:without notice|at any time)",
    ],
    "penalty_cancellation": [
        r"non-?refundable", r"early termination fees?", r"cancellation (?:fees?|charges?)", r"\bno refunds?\b",
        r"forfeit", r"will not be refunded", r"penalty (?:fees?|charges?)", r"late (?:payment )?fees?",
    ],
}

COMPILED = {k: [re.compile(p, re.I) for p in v] for k, v in RULES.items()}

# "We do not sell your data", "we never share ..." should not be flagged.
NEGATION = re.compile(
    r"\b(?:we|company|the company|\w+)\s+(?:do|does|will|shall)\s+not\b|\bwe\s+never\b|\bnever\s+(?:sell|share|rent|trade|charge)\b"
    r"|\bwithout\s+(?:any\s+)?(?:hidden|additional)\s+(?:fees?|charges?)\b|\bno\s+hidden\s+(?:fees?|charges?)\b"
    r"|\bnot\s+(?:automatically\s+)?renew\b|\bwill\s+not\s+be\s+(?:charged|shared|sold)\b",
    re.I,
)
# categories where a negated sentence is normally reassuring, not risky
NEGATION_SENSITIVE = {"data_sharing", "permissions_collection", "auto_renewal", "hidden_fees",
                      "penalty_cancellation"}


def is_negated(clause: str) -> bool:
    return bool(NEGATION.search(clause))


def rule_scan(clause: str):
    """Return a list of findings: category, confidence, source, highlights."""
    findings = []
    negated = is_negated(clause)
    for cat, patterns in COMPILED.items():
        spans = []
        for p in patterns:
            m = p.search(clause)
            if m:
                spans.append(m.group(0))
        if not spans:
            continue
        if negated and cat in NEGATION_SENSITIVE:
            continue
        conf = min(0.95, 0.65 + 0.12 * (len(spans) - 1) + 0.05)
        findings.append({"category": cat, "confidence": round(conf, 3), "source": "rule",
                         "highlights": spans[:3]})
    return findings
