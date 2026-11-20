"""A small Prometheus-compatible metrics exporter using only Python's standard library."""

from __future__ import annotations

import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

START_TIME = time.time()
_REQUESTS_TOTAL = 0
_REQUESTS_LOCK = threading.Lock()


def render_metrics(requests_total: int = 0, start_time_seconds: float | None = None) -> str:
    """Return exporter metrics in Prometheus text exposition format."""
    if requests_total < 0:
        raise ValueError("requests_total cannot be negative")

    start_time = START_TIME if start_time_seconds is None else start_time_seconds
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    lines = [
        "# HELP exporter_up Whether the metrics exporter is running.",
        "# TYPE exporter_up gauge",
        "exporter_up 1",
        "# HELP exporter_http_requests_total Total HTTP requests handled by the exporter.",
        "# TYPE exporter_http_requests_total counter",
        f"exporter_http_requests_total {requests_total}",
        "# HELP exporter_start_time_seconds Unix time when the exporter process started.",
        "# TYPE exporter_start_time_seconds gauge",
        f"exporter_start_time_seconds {start_time:.3f}",
        "# HELP python_info Python runtime version information.",
        "# TYPE python_info gauge",
        f'python_info{{implementation="CPython",version="{version}"}} 1',
        "",
    ]
    return "\n".join(lines)


class MetricsHandler(BaseHTTPRequestHandler):
    """Serve health and metrics endpoints."""

    server_version = "MetricsExporter/1.0"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        global _REQUESTS_TOTAL
        with _REQUESTS_LOCK:
            _REQUESTS_TOTAL += 1
            current_count = _REQUESTS_TOTAL

        route = urlsplit(self.path).path
        if route == "/health":
            body = b'{"status":"ok"}\n'
            content_type = "application/json; charset=utf-8"
            status = 200
        elif route == "/metrics":
            body = render_metrics(current_count).encode("utf-8")
            content_type = "text/plain; version=0.0.4; charset=utf-8"
            status = 200
        else:
            body = b'{"error":"not found"}\n'
            content_type = "application/json; charset=utf-8"
            status = 404

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: object) -> None:
        """Keep request logs short and visible in the Jenkins/local console."""
        print(f"[{self.log_date_time_string()}] {format_string % args}")


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    if not 1 <= port <= 65535:
        raise SystemExit("PORT must be between 1 and 65535")

    server = ThreadingHTTPServer(("0.0.0.0", port), MetricsHandler)
    print(f"Metrics exporter listening on http://0.0.0.0:{port}")
    print(f"Metrics endpoint: http://localhost:{port}/metrics")
    print(f"Health endpoint:  http://localhost:{port}/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping metrics exporter...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
