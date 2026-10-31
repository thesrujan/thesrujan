import os
import time
from threading import Lock

import psutil
from flask import Flask, jsonify, request, Response, g
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Small in-memory catalogue for the lab. Replace with a database in production.
PRODUCTS = {
    "1001": {"name": "Milk", "stock": 18},
    "1002": {"name": "Bread", "stock": 0},
    "1003": {"name": "Eggs", "stock": 42},
    "1004": {"name": "Fruit Box", "stock": 7},
}

REQUESTS = Counter(
    "product_api_requests_total",
    "Total product API requests",
    ["endpoint", "method", "status"],
)
REQUEST_DURATION = Histogram(
    "product_api_request_duration_seconds",
    "Product API request duration in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)
PRODUCT_AVAILABLE = Gauge(
    "product_available",
    "Whether a product is available (1=yes, 0=no)",
    ["product_id"],
)

for product_id, product in PRODUCTS.items():
    PRODUCT_AVAILABLE.labels(product_id=product_id).set(1 if product["stock"] > 0 else 0)

# Demo-only memory allocation. Enabled by DEMO_MODE in the Kubernetes Deployment.
_demo_allocations = []
_demo_lock = Lock()


def _update_product_gauges():
    for product_id, product in PRODUCTS.items():
        PRODUCT_AVAILABLE.labels(product_id=product_id).set(1 if product["stock"] > 0 else 0)


@app.before_request
def start_timer():
    g.request_started_at = time.perf_counter()


@app.after_request
def record_request(response):
    if request.path != "/metrics":
        endpoint = request.endpoint or "unknown"
        REQUESTS.labels(endpoint=endpoint, method=request.method, status=str(response.status_code)).inc()
        elapsed = time.perf_counter() - getattr(g, "request_started_at", time.perf_counter())
        REQUEST_DURATION.labels(endpoint=endpoint).observe(elapsed)
    return response


@app.get("/")
def home():
    return jsonify({
        "service": "quick-commerce-product-api",
        "message": "Product availability API is running",
        "pod": os.getenv("POD_NAME", "local"),
        "endpoints": [
            "/api/products/<product_id>/availability",
            "/health",
            "/metrics",
        ],
    })


@app.get("/api/products/<product_id>/availability")
def product_availability(product_id):
    product = PRODUCTS.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found", "product_id": product_id}), 404

    # Optional small CPU workload for repeat-request demonstrations (0-100 ms/request).
    work_ms = request.args.get("work_ms", default=0, type=int)
    work_ms = max(0, min(work_ms, 100))
    end_at = time.perf_counter() + (work_ms / 1000.0)
    value = 0
    while time.perf_counter() < end_at:
        value = (value * 33 + 17) % 1000003

    available = product["stock"] > 0
    PRODUCT_AVAILABLE.labels(product_id=product_id).set(1 if available else 0)
    return jsonify({
        "product_id": product_id,
        "product_name": product["name"],
        "available": available,
        "stock": product["stock"],
        "served_by_pod": os.getenv("POD_NAME", "local"),
    })


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "pod": os.getenv("POD_NAME", "local")})


@app.get("/metrics")
def metrics():
    # prometheus_client's default registry exposes process metrics on Linux,
    # including process_resident_memory_bytes and process_cpu_seconds_total.
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get("/demo/allocate-memory")
def allocate_demo_memory():
    if os.getenv("DEMO_MODE", "false").lower() != "true":
        return jsonify({"error": "Demo endpoint is disabled"}), 403

    mb = request.args.get("mb", default=32, type=int)
    if mb < 1 or mb > 48:
        return jsonify({"error": "Choose a value between 1 and 48 MB"}), 400

    # Touch one byte per page so RSS reflects the allocation for the memory alert.
    block = bytearray(mb * 1024 * 1024)
    for offset in range(0, len(block), 4096):
        block[offset] = 1
    with _demo_lock:
        _demo_allocations.append(block)

    rss = psutil.Process().memory_info().rss
    return jsonify({
        "message": "Demo memory allocated",
        "allocated_mb": mb,
        "process_rss_mb": round(rss / (1024 * 1024), 2),
        "note": "This lab-only allocation is held in this Pod to demonstrate a Prometheus alert.",
    })


@app.get("/demo/release-memory")
def release_demo_memory():
    if os.getenv("DEMO_MODE", "false").lower() != "true":
        return jsonify({"error": "Demo endpoint is disabled"}), 403
    with _demo_lock:
        _demo_allocations.clear()
    return jsonify({"message": "Demo allocations released; restart the Pod if RSS does not fall."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
