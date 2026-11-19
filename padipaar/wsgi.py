from app.main import app  # noqa: F401  (gunicorn entry point: wsgi:app)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
