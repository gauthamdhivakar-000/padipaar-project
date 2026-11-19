"""Tiny SQLite store for the public score board (no user documents are ever stored)."""
import datetime
import json
import os
import sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "data", "padipaar.db"))


def _con():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = _con()
    try:
        con.execute(
            """CREATE TABLE IF NOT EXISTS app_scores(
                slug TEXT PRIMARY KEY, app_name TEXT NOT NULL, category TEXT NOT NULL,
                terms_url TEXT, score INTEGER NOT NULL, band TEXT NOT NULL,
                top_categories TEXT NOT NULL, clause_count INTEGER NOT NULL,
                is_sample INTEGER NOT NULL DEFAULT 0, analysed_on TEXT NOT NULL)"""
        )
        con.commit()
    finally:
        con.close()


def count_scores():
    con = _con()
    try:
        return con.execute("SELECT COUNT(*) FROM app_scores").fetchone()[0]
    finally:
        con.close()


def upsert_score(slug, app_name, category, terms_url, result, is_sample=False):
    top = [c["category"] for c in result.get("categories", [])][:3]
    con = _con()
    try:
        con.execute(
            "REPLACE INTO app_scores(slug,app_name,category,terms_url,score,band,top_categories,"
            "clause_count,is_sample,analysed_on) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (slug, app_name, category, terms_url, int(result["score"]), result["band"],
             json.dumps(top), int(result.get("clause_count", 0)), 1 if is_sample else 0,
             datetime.date.today().isoformat()),
        )
        con.commit()
    finally:
        con.close()


def _row(r):
    d = dict(r)
    d["top_categories"] = json.loads(d["top_categories"])
    d["is_sample"] = bool(d["is_sample"])
    return d


def list_scores(category=None):
    con = _con()
    try:
        if category:
            rows = con.execute("SELECT * FROM app_scores WHERE category=? ORDER BY score DESC", (category,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM app_scores ORDER BY score DESC").fetchall()
        return [_row(r) for r in rows]
    finally:
        con.close()


def get_score(slug):
    con = _con()
    try:
        r = con.execute("SELECT * FROM app_scores WHERE slug=?", (slug,)).fetchone()
        return _row(r) if r else None
    finally:
        con.close()
