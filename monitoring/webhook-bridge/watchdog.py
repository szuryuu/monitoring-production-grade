import httpx, time, os

PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
ALERTMANAGER_URL = os.environ.get("ALERTMANAGER_URL", "http://alertmanager:9093")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "15"))


def is_prometheus_up():
    try:
        r = httpx.get(f"{PROMETHEUS_URL}/-/healthy", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def send_alert(firing: bool):
    status = "firing" if firing else "resolved"
    payload = [
        {
            "status": status,
            "labels": {
                "alertname": "PrometheusDown",
                "instance": "prometheus:9090",
                "severity": "critical",
            },
            "annotations": {"summary": "Prometheus is down on prometheus:9090"},
            "generatorURL": "http://watchdog",
        }
    ]
    try:
        httpx.post(f"{ALERTMANAGER_URL}/api/v2/alerts", json=payload, timeout=5)
        print(f"[watchdog] Sent {status} alert to Alertmanager")
    except Exception as e:
        print(f"[watchdog] Failed to send alert: {e}")


was_down = False

print(f"[watchdog] Starting. Checking Prometheus every {CHECK_INTERVAL}s")
while True:
    up = is_prometheus_up()
    if not up and not was_down:
        print("[watchdog] Prometheus is DOWN — sending firing alert")
        send_alert(firing=True)
        was_down = True
    elif up and was_down:
        print("[watchdog] Prometheus is UP — sending resolved alert")
        send_alert(firing=False)
        was_down = False
    time.sleep(CHECK_INTERVAL)
