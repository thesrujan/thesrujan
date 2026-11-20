from threading import Thread
from urllib.request import urlopen

from http.server import ThreadingHTTPServer

from metrics_exporter import MetricsHandler, render_metrics


def test_render_metrics_contains_exporter_status():
    output = render_metrics(requests_total=3, start_time_seconds=1234.5)
    assert "# TYPE exporter_up gauge" in output
    assert "exporter_up 1" in output


def test_render_metrics_reports_request_count():
    output = render_metrics(requests_total=7, start_time_seconds=1234.5)
    assert "exporter_http_requests_total 7" in output


def test_render_metrics_reports_start_time_and_python_version():
    output = render_metrics(requests_total=0, start_time_seconds=1234.5)
    assert "exporter_start_time_seconds 1234.500" in output
    assert 'python_info{implementation="CPython",version="' in output


def test_render_metrics_rejects_negative_request_count():
    try:
        render_metrics(requests_total=-1)
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError("Expected ValueError for a negative request count")


def test_http_health_and_metrics_endpoints():
    server = ThreadingHTTPServer(("127.0.0.1", 0), MetricsHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{base_url}/health", timeout=3) as response:
            assert response.status == 200
            assert response.read().decode("utf-8").strip() == '{"status":"ok"}'

        with urlopen(f"{base_url}/metrics", timeout=3) as response:
            metrics = response.read().decode("utf-8")
            assert response.status == 200
            assert "exporter_up 1" in metrics
    finally:
        server.shutdown()
        worker.join(timeout=3)
        server.server_close()
