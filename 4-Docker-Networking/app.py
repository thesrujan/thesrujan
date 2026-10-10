from flask import Flask, jsonify
import socket

app = Flask(__name__)


def check_tcp_service(host: str, port: int) -> dict:
    """Check whether a service name resolves and its TCP port is reachable."""
    try:
        with socket.create_connection((host, port), timeout=2):
            return {"host": host, "port": port, "reachable": True, "status": "connected"}
    except Exception as exc:
        return {"host": host, "port": port, "reachable": False, "status": str(exc)}


@app.get("/")
def homepage():
    return jsonify({
        "message": "Docker Networking Lab",
        "endpoints": ["/about", "/health", "/connectivity"],
    })


@app.get("/about")
def about():
    return jsonify({
        "name": "Simple REST API",
        "version": "1.0",
        "description": "A Flask API running alongside MySQL and Redis on a user-defined Docker bridge network.",
    })


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "container": socket.gethostname()})


@app.get("/connectivity")
def connectivity():
    results = {
        "mysql": check_tcp_service("mysql", 3306),
        "redis": check_tcp_service("redis", 6379),
    }
    return jsonify({"container": socket.gethostname(), "services": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
