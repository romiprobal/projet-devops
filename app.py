import os

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)


def database_ok():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        return False
    try:
        with psycopg.connect(dsn, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False


@app.route("/health")
def health():
    if database_ok():
        return jsonify(status="healthy", database="ok"), 200
    return jsonify(status="degraded", database="unreachable"), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)