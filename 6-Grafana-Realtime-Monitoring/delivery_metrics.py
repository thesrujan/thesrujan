"""Simulate quick-commerce delivery metrics and expose them for Prometheus."""
from prometheus_client import start_http_server, Summary, Gauge
import random
import time

TOTAL_DELIVERIES = Gauge("total_deliveries", "Total number of deliveries in the current sample")
PENDING_DELIVERIES = Gauge("pending_deliveries", "Number of pending deliveries")
ON_THE_WAY_DELIVERIES = Gauge("on_the_way_deliveries", "Number of deliveries on the way")
AVERAGE_DELIVERY_TIME = Summary("average_delivery_time", "Observed delivery time in seconds")


def simulate_delivery() -> None:
    # Pending is usually between 10 and 20 so the warning rule can fire.
    pending = random.randint(10, 20)
    on_the_way = random.randint(5, 20)
    delivered = random.randint(30, 70)
    delivery_time = random.uniform(15, 45)
    total = pending + on_the_way + delivered

    TOTAL_DELIVERIES.set(total)
    PENDING_DELIVERIES.set(pending)
    ON_THE_WAY_DELIVERIES.set(on_the_way)
    AVERAGE_DELIVERY_TIME.observe(delivery_time)

    print(
        f"[DEBUG] total={total}, pending={pending}, "
        f"on_the_way={on_the_way}, delivery_time={delivery_time:.2f}s",
        flush=True,
    )


if __name__ == "__main__":
    port = 8000
    print(f"[INFO] Starting Prometheus metrics server on 0.0.0.0:{port}", flush=True)
    start_http_server(port, addr="0.0.0.0")
    while True:
        simulate_delivery()
        time.sleep(1)
