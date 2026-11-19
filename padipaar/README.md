# PadiPaar - Read What You Sign

Dark-pattern and hidden-clause detector in Tamil.
Paste a terms page, enter a URL or upload a PDF -> PadiPaar splits it into clauses, finds the risky ones,
gives a 0-100 risk score and explains every warning in simple Tamil (with the original clause shown beside it).
A browser extension also checks the sign-up page itself for dark patterns (pre-ticked consent boxes,
urgency pressure, hidden "No thanks" buttons).

**One deployable service**: the Flask backend also serves the web app, so there is no separate frontend build.

```
padipaar/
  app/                 backend (Flask)
    main.py            API + web app server, rate limiting, security headers
    extractor.py       text / URL (SSRF-safe) / PDF -> clauses
    rules.py           regex rule engine with negation guard
    train.py           trains the TF-IDF + Logistic Regression classifier
    classifier.py      hybrid detector (rules + ML)
    scoring.py         0-100 score + Low / Medium / High
    explainer.py       Tamil + English explanations
    explanations_ta.json   all Tamil / English text (edit here)
    training_data.py   seed training set
    samples.py         demo documents (invented, not real companies)
    db.py              SQLite score board (no user documents are stored)
  static/              web app (index.html, styles.css, app.js)
  extension/           Chrome / Brave extension (Manifest V3)
  tests/               25 automated tests
  scripts/             seed_scores.py + apps.csv
  Dockerfile  Procfile  render.yaml  requirements.txt  wsgi.py
```

## 1. Run on your computer (5 minutes)

Requires Python 3.11 or newer (3.12 recommended).

```bash
cd padipaar
python -m venv venv
# Windows:  venv\Scripts\activate        Mac/Linux:  source venv/bin/activate
pip install -r requirements.txt
python -m app.train          # trains the model (a few seconds)
python wsgi.py               # opens on http://127.0.0.1:5000
```

Open http://127.0.0.1:5000 in your browser. Click one of the "Try a sample" buttons to see it work.

If you skip `python -m app.train`, the app trains the model automatically on first start.

Run the tests: `python -m unittest discover -s tests -v`

## 2. Deploy (free) on Render - recommended

1. Create a GitHub account and a new **empty repository** named `padipaar`.
2. Upload this whole folder to it (GitHub website -> "Add file" -> "Upload files", or use git).
3. Go to https://render.com -> sign in with GitHub -> **New +** -> **Blueprint** -> pick your repo.
   Render reads `render.yaml` and sets everything up (build, start command, health check).
   *(Alternative: New + -> Web Service -> pick repo -> Runtime Python ->
   Build `pip install -r requirements.txt && python -m app.train` ->
   Start `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`.)*
4. Wait for the first deploy (3-6 minutes). Your site is at `https://<name>.onrender.com`.
5. Open `https://<name>.onrender.com/health` -> you should see `{"status":"ok"}`.

Notes
- Free instances sleep when idle: open the site 2 minutes before a demo so it is awake.
- The free plan's disk is temporary; the demo score board is re-created automatically on every start.

### Other hosts
- **Docker** (Hugging Face Spaces Docker, Railway, Fly.io, any VPS):
  `docker build -t padipaar . && docker run -p 10000:10000 padipaar` then open http://localhost:10000
  (Hugging Face Spaces: set `PORT` to `7860`.)
- **Heroku / Railway (Procfile)**: the included `Procfile` works as is.

## 3. Install the browser extension (Chrome / Brave / Edge)

1. Open `brave://extensions` (or `chrome://extensions`) and switch on **Developer mode**.
2. Click **Load unpacked** and choose the `extension` folder.
3. Click the PadiPaar icon -> open **Settings** -> paste your server address
   (`https://<name>.onrender.com`, or `http://127.0.0.1:5000` when running locally) -> **Save**.
4. Open any terms or sign-up page and click **Scan this page**.

## 4. API reference

| Method | Path | Body / notes |
|---|---|---|
| GET | `/health` | status |
| POST | `/api/analyze` | `{"text": "..."}` or `{"url": "https://..."}`; optional `ui_findings` |
| POST | `/api/analyze/pdf` | multipart form field `file` (PDF, max 8 MB) |
| GET | `/api/scores?category=` | public score board |
| GET | `/api/scores/<slug>` | one entry |
| GET | `/api/samples` | demo documents |
| GET | `/api/model-info` | categories + validation metrics |
| POST | `/api/admin/scores` | header `X-Admin-Key`; disabled unless `ADMIN_KEY` is set |

## 5. Add real apps to the Compare page

1. In Render -> Environment add `ADMIN_KEY` = a long random secret.
2. Edit `scripts/apps.csv` (slug, app_name, category, terms_url).
3. Run: `python scripts/seed_scores.py https://<name>.onrender.com <ADMIN_KEY> scripts/apps.csv`
   For sites that cannot be fetched automatically, save the copied terms text as `scripts/texts/<slug>.txt`.

Only add pages that are publicly visible, and keep the "automated analysis, not legal advice" note.

## 6. Improve the model (important for honest accuracy)

The built-in training set is a small hand-written **seed set** (about 180 clauses). The validation numbers
shown on the About page come from cross-validation on that seed set and are therefore optimistic.
To get real numbers:
1. Collect 300-500 real clauses from terms pages, label them, and add them to `app/training_data.py`
   (or load a CSV in `app/train.py`).
2. Keep a separate test set of clauses the model never trains on and report results on that.
3. Re-run `python -m app.train` and commit the updated code.

## 7. How the pipeline works

1. Input (text / URL / PDF) -> `extractor.py` cleans it and splits it into clauses.
2. Each clause goes through the **rule engine** (regex + negation guard, e.g. "We do not sell your data" is not flagged)
   and the **ML classifier**; results are merged (a clause found by both gets a confidence boost).
3. `scoring.py` takes the highest confidence per category, multiplies by the category weight (weights sum to 100),
   adds a small bonus for dark-pattern findings from the extension (max 15), and returns 0-100:
   Low 0-20, Medium 21-50, High 51-100.
4. `explainer.py` attaches Tamil and English explanations, tips and extracted details (amounts, durations).

## 8. Safety and privacy built in
- Submitted documents are processed in memory and **not stored**; only the demo/admin score board is saved.
- URL fetching blocks private/local addresses (SSRF protection), limits redirects and download size.
- Input size limits, per-visitor rate limiting, security headers and a content-security policy.
- This tool highlights risk with automated analysis. **It is not legal advice.**

## 9. Troubleshooting
| Problem | Fix |
|---|---|
| `pip install` fails on scikit-learn | Use Python 3.11+ and upgrade pip: `python -m pip install --upgrade pip` |
| Port already in use | `PORT=5001 python wsgi.py` (Windows PowerShell: `$env:PORT=5001; python wsgi.py`) |
| Render build fails | Check the Python version is 3.12 (`PYTHON_VERSION` in `render.yaml`) |
| Site slow on first open | Free instance was asleep - wait ~30 seconds |
| URL analysis says "paste the text" | The site needs JavaScript or blocks bots; copy the terms text instead |
| Extension says it cannot reach the service | Check the server address in the extension Settings |
