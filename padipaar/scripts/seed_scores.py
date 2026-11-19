"""Add real app scores to the public score board.

Usage:
  set ADMIN_KEY on the server first (Render -> Environment), then:
  python scripts/seed_scores.py https://YOUR-APP.onrender.com YOUR_ADMIN_KEY scripts/apps.csv

CSV columns: slug,app_name,category,terms_url
If a page cannot be fetched (JavaScript-only sites), put the copied terms text in a file named
scripts/texts/<slug>.txt and the script will upload that text instead.
"""
import csv
import os
import sys
import time

import requests


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    base, key, path = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
    here = os.path.dirname(os.path.abspath(__file__))
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            slug = row["slug"].strip()
            payload = {"slug": slug, "app_name": row["app_name"].strip(),
                       "category": row.get("category", "other").strip() or "other",
                       "terms_url": row.get("terms_url", "").strip()}
            txt = os.path.join(here, "texts", slug + ".txt")
            if os.path.exists(txt):
                with open(txt, encoding="utf-8") as t:
                    payload["text"] = t.read()
            try:
                r = requests.post(base + "/api/admin/scores", json=payload,
                                  headers={"X-Admin-Key": key}, timeout=90)
                print(slug, r.status_code, r.json())
            except Exception as exc:  # keep going with the next app
                print(slug, "FAILED:", exc)
            time.sleep(2)  # be polite to the websites


if __name__ == "__main__":
    main()
