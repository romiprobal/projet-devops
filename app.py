import os
import time
import psycopg
from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

#Compteur : nombre total de requêtes, par route et par code HTTP
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Nombre total de requetes HTTP recues",
    ["endpoint", "code"],
)

#Histogramme : durée des requêtes, par route (permet p95 / p99)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Duree de traitement d'une requete HTTP en secondes",
    ["endpoint"],
)

#Jauge : version et SHA déployés (vaut toujours 1, l'info est dans les labels)
BUILD_INFO = Gauge(
    "app_build_info",
    "Version et SHA du commit deploye",
    ["version", "git_sha"],
)
BUILD_INFO.labels(
    version=os.getenv("APP_VERSION", "0.0.0-dev"),
    git_sha=os.getenv("GIT_SHA", "unknown"),
).set(1)


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

    
#2 hook mesurent chaque requete
@app.before_request
def start_timer():
    g.start_time = time.perf_counter()


@app.after_request
def record_metrics(response):
    if request.path == "/metrics":
        return response  # on ne mesure pas le scrape lui-même
    endpoint = request.url_rule.rule if request.url_rule else "unmatched"
    duration = time.perf_counter() - g.start_time
    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)
    REQUEST_COUNT.labels(endpoint=endpoint, code=response.status_code).inc()
    return response



@app.route("/health")
def health():
    if database_ok():
        return jsonify(status="healthy", database="ok"), 200
    return jsonify(status="degraded", database="unreachable"), 503

@app.route("/boom")
def boom():
    return jsonify(error="erreur simulee pour tester l'alerte"), 500

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)