from prometheus_client import start_http_server, Counter, Gauge
import random
import time

REQUESTS = Counter(
    "demo_requests_total",
    "Total number of demo requests"
)

TEMPERATURE = Gauge(
    "demo_temperature_celsius",
    "Demo temperature value"
)

if __name__ == "__main__":
    # Metrics endpoint on :8000/metrics
    start_http_server(8000)

    print("Metrics available at http://localhost:8000/metrics")

    while True:
        REQUESTS.inc()
        TEMPERATURE.set(random.uniform(20.0, 35.0))
        time.sleep(5)