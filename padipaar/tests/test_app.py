"""Run all tests:  python -m unittest discover -s tests -v"""
import io
import json
import os
import sys
import tempfile
import unittest

# use a throw-away database for tests
_TMP = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(_TMP, "test.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import extractor, rules, scoring, explainer  # noqa: E402
from app.main import app  # noqa: E402
import app.main as main_module  # noqa: E402
from app.classifier import analyse_clause  # noqa: E402
from app.samples import SAMPLES  # noqa: E402


class ExtractorTests(unittest.TestCase):
    def test_split_clauses_basic(self):
        text = SAMPLES[0]["text"]
        clauses = extractor.split_clauses(text)
        self.assertGreater(len(clauses), 8)
        self.assertTrue(all(40 <= len(c) <= 1200 for c in clauses))

    def test_split_skips_short_and_dedupes(self):
        text = "Hi. " + "This is a perfectly normal sentence that is long enough to keep. " * 3
        clauses = extractor.split_clauses(text)
        self.assertEqual(len(clauses), 1)

    def test_html_to_text_removes_scripts(self):
        html = "<html><script>alert(1)</script><body><p>Hello terms</p><footer>x</footer></body></html>"
        out = extractor.html_to_text(html)
        self.assertIn("Hello terms", out)
        self.assertNotIn("alert", out)

    def test_url_guard_blocks_private_and_bad_schemes(self):
        for bad in ["http://localhost/x", "http://127.0.0.1/", "http://10.0.0.5/", "http://192.168.1.1/",
                    "http://169.254.169.254/latest/meta-data", "file:///etc/passwd", "ftp://example.com/x",
                    "javascript:alert(1)", "", "not a url", "http://[::1]/"]:
            with self.assertRaises(extractor.InputError, msg=bad):
                extractor.check_url_is_safe(bad)

    def test_bad_pdf_rejected(self):
        with self.assertRaises(extractor.InputError):
            extractor.pdf_to_text(b"%PDF-1.4 not really a pdf")


class RuleTests(unittest.TestCase):
    CASES = {
        "auto_renewal": "Your subscription will automatically renew each month until you cancel.",
        "hidden_fees": "Additional fees may apply and we may change our prices at any time.",
        "data_sharing": "We may share your personal information with third-party partners and advertisers.",
        "permissions_collection": "The app requires access to your contacts and SMS messages.",
        "liability_limit": "In no event shall the company be liable for any damages.",
        "arbitration_waiver": "Any dispute will be resolved through binding arbitration.",
        "unilateral_change": "We may modify these terms at any time without prior notice.",
        "penalty_cancellation": "All payments are non-refundable and an early termination fee applies.",
    }

    def test_each_category_detected(self):
        for cat, sentence in self.CASES.items():
            cats = {f["category"] for f in rules.rule_scan(sentence)}
            self.assertIn(cat, cats, cat)

    def test_negation_guard(self):
        for safe in ["We do not sell your personal data to anyone.",
                     "We never share your data with advertisers.",
                     "There are no hidden fees in our pricing.",
                     "Your plan will not renew automatically."]:
            self.assertEqual(rules.rule_scan(safe), [], safe)

    def test_highlights_present(self):
        f = rules.rule_scan(self.CASES["arbitration_waiver"])[0]
        self.assertTrue(f["highlights"])


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(scoring.WEIGHTS.values()), 100)

    def test_empty_is_zero_low(self):
        r = scoring.compute_score([])
        self.assertEqual((r["score"], r["band"]), (0, "Low"))

    def test_max_per_category_and_cap(self):
        f = [{"category": c, "confidence": 1.0} for c in scoring.WEIGHTS]
        r = scoring.compute_score(f, [{"type": "pre_ticked_consent"}, {"type": "urgency_pressure"},
                                      {"type": "hidden_decline"}])
        self.assertEqual(r["score"], 100)
        self.assertEqual(r["ui_bonus"], scoring.UI_BONUS_CAP)

    def test_bands(self):
        self.assertEqual(scoring.band_for(20), "Low")
        self.assertEqual(scoring.band_for(21), "Medium")
        self.assertEqual(scoring.band_for(50), "Medium")
        self.assertEqual(scoring.band_for(51), "High")


class ExplainerTests(unittest.TestCase):
    def test_all_categories_have_tamil_and_english(self):
        self.assertEqual(set(explainer.EXPL["categories"]), set(rules.CATEGORIES))
        for c, e in explainer.EXPL["categories"].items():
            for k in ("title_en", "title_ta", "meaning_en", "meaning_ta", "tip_en", "tip_ta"):
                self.assertTrue(e[k].strip(), (c, k))
            self.assertTrue(any("\u0b80" <= ch <= "\u0bff" for ch in e["meaning_ta"]), c)

    def test_detail_extraction(self):
        f = explainer.explain_finding({"category": "hidden_fees", "confidence": 0.9, "source": "rule"},
                                      "A fee of Rs. 499 applies for 30 days.")
        self.assertIn("Rs. 499", f["details"])
        self.assertIn("30 days", f["details"])


class ClassifierTests(unittest.TestCase):
    def test_unseen_risky_and_safe(self):
        risky = analyse_clause("The app will read your contact list and SMS inbox.")
        self.assertIn("permissions_collection", {f["category"] for f in risky})
        safe = analyse_clause("Our team in Madurai answers every query within one working day.")
        self.assertEqual(safe, [])


class ApiTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = False  # exercise the real error handlers
        self.c = app.test_client()
        main_module._hits.clear()

    def test_health_and_index(self):
        self.assertEqual(self.c.get("/health").get_json()["status"], "ok")
        self.assertEqual(self.c.get("/api/health").status_code, 200)
        with self.c.get("/") as r:
            self.assertEqual(r.status_code, 200)
            self.assertIn(b"PadiPaar", r.data)
            self.assertIn("Content-Security-Policy", r.headers)
        for path in ("/static/app.js", "/static/styles.css"):
            with self.c.get(path) as r:
                self.assertEqual(r.status_code, 200, path)

    def test_analyze_risky_and_friendly(self):
        hi = self.c.post("/api/analyze", json={"text": SAMPLES[0]["text"]}).get_json()
        self.assertEqual(hi["band"], "High")
        self.assertGreater(hi["clause_count"], 8)
        self.assertTrue(hi["findings"][0]["title_ta"])
        lo = self.c.post("/api/analyze", json={"text": SAMPLES[2]["text"]}).get_json()
        self.assertEqual(lo["band"], "Low")
        self.assertEqual(lo["findings"], [])

    def test_ui_findings_validated(self):
        body = {"text": SAMPLES[1]["text"], "ui_findings": [{"type": "pre_ticked_consent", "text": "x"},
                                                            {"type": "evil"}, "junk", 5]}
        r = self.c.post("/api/analyze", json=body).get_json()
        self.assertEqual([u["type"] for u in r["ui_findings"]], ["pre_ticked_consent"])
        self.assertEqual(r["ui_bonus"], 8)

    def test_bad_requests(self):
        cases = [
            ({"json": None}, 400), ({"json": {}}, 400), ({"json": {"text": "   "}}, 400),
            ({"json": {"text": "short"}}, 400), ({"json": {"text": "x" * 200_001}}, 400),
            ({"json": {"url": "http://localhost/"}}, 400), ({"json": {"url": "ftp://x.com/a"}}, 400),
            ({"json": {"text": 123}}, 400),
        ]
        for kwargs, code in cases:
            r = self.c.post("/api/analyze", **({"json": kwargs["json"]} if kwargs["json"] is not None
                                               else {"data": "not json", "content_type": "text/plain"}))
            self.assertEqual(r.status_code, code, kwargs)
            self.assertIn("error", r.get_json())

    def test_pdf_upload(self):
        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest("reportlab not installed")
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        y = 800
        import textwrap
        for line in textwrap.wrap(SAMPLES[1]["text"], 90):
            c.drawString(40, y, line)
            y -= 14
        c.save()
        r = self.c.post("/api/analyze/pdf", data={"file": (io.BytesIO(buf.getvalue()), "t.pdf")},
                        content_type="multipart/form-data")
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        self.assertEqual(r.get_json()["band"], "High")

    def test_pdf_errors(self):
        r = self.c.post("/api/analyze/pdf", data={}, content_type="multipart/form-data")
        self.assertEqual(r.status_code, 400)
        r = self.c.post("/api/analyze/pdf", data={"file": (io.BytesIO(b"hello"), "t.pdf")},
                        content_type="multipart/form-data")
        self.assertEqual(r.status_code, 400)
        big = io.BytesIO(b"%PDF" + b"0" * (9 * 1024 * 1024))
        r = self.c.post("/api/analyze/pdf", data={"file": (big, "big.pdf")}, content_type="multipart/form-data")
        self.assertEqual(r.status_code, 413)

    def test_scores_and_samples(self):
        d = self.c.get("/api/scores").get_json()
        self.assertGreaterEqual(len(d["scores"]), 3)
        demo = [s for s in d["scores"] if s["slug"].startswith("demo-")]
        self.assertEqual(len(demo), 3)
        self.assertTrue(all(s["is_sample"] for s in demo))
        only = self.c.get("/api/scores?category=loan").get_json()["scores"]
        self.assertTrue(only and all(s["category"] == "loan" for s in only))
        self.assertEqual(self.c.get("/api/scores/demo-quickcash-loan").status_code, 200)
        self.assertEqual(self.c.get("/api/scores/nope").status_code, 404)
        self.assertEqual(len(self.c.get("/api/samples").get_json()), 3)
        self.assertIn("macro_f1", self.c.get("/api/model-info").get_json()["model"])

    def test_admin_endpoint(self):
        body = {"slug": "my-app", "app_name": "My App", "category": "test", "text": SAMPLES[1]["text"]}
        main_module.ADMIN_KEY = ""
        self.assertEqual(self.c.post("/api/admin/scores", json=body).status_code, 403)
        main_module.ADMIN_KEY = "secret123"
        try:
            self.assertEqual(self.c.post("/api/admin/scores", json=body,
                                         headers={"X-Admin-Key": "wrong"}).status_code, 403)
            ok = self.c.post("/api/admin/scores", json=body, headers={"X-Admin-Key": "secret123"})
            self.assertEqual(ok.status_code, 200, ok.get_data(as_text=True))
            self.assertEqual(self.c.get("/api/scores/my-app").get_json()["app_name"], "My App")
            bad = self.c.post("/api/admin/scores", json=dict(body, slug="Bad Slug!"),
                              headers={"X-Admin-Key": "secret123"})
            self.assertEqual(bad.status_code, 400)
        finally:
            main_module.ADMIN_KEY = ""

    def test_rate_limit(self):
        old = main_module.RATE_LIMIT
        main_module.RATE_LIMIT = 3
        try:
            codes = [self.c.post("/api/analyze", json={"text": SAMPLES[2]["text"]}).status_code for _ in range(5)]
            self.assertEqual(codes[:3], [200, 200, 200])
            self.assertEqual(codes[3:], [429, 429])
        finally:
            main_module.RATE_LIMIT = old
            main_module._hits.clear()

    def test_cors_and_unknown_route(self):
        r = self.c.options("/api/analyze", headers={"Origin": "chrome-extension://abc"})
        self.assertIn(r.status_code, (200, 204))
        self.assertEqual(r.headers.get("Access-Control-Allow-Origin"), "*")
        r = self.c.get("/api/nope")
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.get_json())
        r = self.c.get("/api/analyze")
        self.assertEqual(r.status_code, 405)


if __name__ == "__main__":
    unittest.main()
