from fastapi import FastAPI, Request
import os, httpx, uvicorn

SLACK_ALERT_WEBHOOK_URL = os.environ.get(
    "SLACK_ALERT_WEBHOOK_URL", os.environ["SLACK_INCOMING_WEBHOOK_URL"]
)
app = FastAPI()
SLACK_WEBHOOK_URL = os.environ["SLACK_INCOMING_WEBHOOK_URL"]
INCIDENTFOX_URL = os.environ.get("INCIDENTFOX_URL", "http://incidentfox-sre-agent:8000")

PROMPTS = {
    "PrometheusDown": (
        "We have a critical alert: Prometheus is DOWN on {instance}. Metrics collection has stopped. "
        "Do NOT use Prometheus or VictoriaMetrics as they may be unavailable. "
        "Step 1: Run 'docker logs prometheus --tail=20' to check why Prometheus is down. Show EXACT output. "
        "Step 2: Run 'docker inspect prometheus --format={{{{.State.Status}}}}' to check container state. "
        "Step 3: Use Loki to fetch 5 most recent log lines containing 'prometheus' OR 'FATAL' OR 'error' "
        'from {{host="mopogra-vm"}} in last 10 minutes. Show EXACT full text. '
        "Step 4: Based on findings, attempt to restart prometheus with 'docker start prometheus'. "
        "Step 5: Write RCA explaining root cause. If restart failed, explain why and what manual intervention is needed."
    ),
    "NodeExporterDown": (
        "We have a critical alert: Node Exporter is DOWN on {instance}. Host metrics collection has stopped. "
        "Step 1: Run 'docker logs node-exporter --tail=20' to check last known state. Show EXACT output. "
        "Step 2: Run this exact bash command to fetch Loki logs: "
        "python .claude/skills/observability-loki/scripts/query_logs.py "
        '\'{{job="syslog", host="mopogra-vm"}} |~ "FATAL"\' --limit 5 --lookback 0.5 '
        "Show EXACT full output. If no logs found, state that explicitly. "
        "Step 3: Run 'docker start node-exporter' to restart. Show exact output. "
        "Step 4: Write RCA using ONLY exact values from Step 1 and 2. Do NOT use placeholders."
    ),
    "HighMemoryUsage": (
        "We have a critical alert: HighMemoryUsage on {instance}. {summary}. "
        "Do NOT use CloudWatch or any external tools. Show ALL raw values. "
        "Step 1: Use VictoriaMetrics to query instant value of node_memory_MemAvailable_bytes "
        'and node_memory_MemTotal_bytes for label {{instance="node-exporter:9100"}}. '
        "Show EXACT numeric values and calculate used percentage. "
        "Step 2: Use Loki to fetch 5 most recent log lines containing 'OOM' OR 'FATAL' OR 'killed' "
        'using label selector {{host="mopogra-vm"}} lookback=0.5 hours. Show EXACT full text. '
        "Step 3: Identify which process is consuming memory. "
        "Step 4: Attempt to kill the process if possible. If not, provide exact commands for the user to run."
    ),
    "HighCPUUsage": (
        "We have a critical alert: HighCPUUsage on {instance}. {summary}. "
        "Do NOT use CloudWatch, New Relic, or any external tools. Show ALL raw values. "
        'Step 1: Use VictoriaMetrics to query instant value of node_load1 for label {{instance="{instance}"}}. Show EXACT numeric value. '
        "Step 2: Use Loki to fetch EXACTLY 3 most recent log lines containing 'FATAL' "
        'using label selector {{job="syslog", host="mopogra-vm"}} in last 10 minutes. Show EXACT full text. '
        "Step 3: Write brief objective RCA using EXACT values from Step 1 and Step 2."
    ),
}

DEFAULT_PROMPT = (
    "We have a critical alert: {name} on {instance}. {summary}. "
    "Step 1: Use Loki to fetch 5 most recent relevant log lines from host mopogra-vm in the last 10 minutes. Show EXACT full text. "
    "Step 2: Write a brief RCA and recommended remediation steps."
)


async def _trigger_investigate(url: str, prompt: str, thread_id: str, alert_name: str):
    try:
        result_text = ""
        success = False

        async with httpx.AsyncClient(timeout=600) as client:
            async with client.stream(
                "POST",
                f"{url}/investigate",
                json={"prompt": prompt, "thread_id": thread_id},
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json

                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "result":
                                data = event.get("data", {})
                                result_text = data.get("text", "")
                                success = data.get("success", False)
                        except Exception:
                            pass

        if result_text:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    SLACK_ALERT_WEBHOOK_URL,
                    json={
                        "text": f":mag: *[AUTO INVESTIGATION RESULT] {alert_name}*\n\n{result_text[:4000]}"
                    },
                )

        from datetime import datetime, timezone

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        runbook_path = f"/home/agent/runbooks/{alert_name}/{date_str}_runbook.md"
        runbook_prompt = (
            f"Based on the investigation above, generate a runbook and save it to {runbook_path}. "
            f"Include these sections: "
            f"1. Incident Summary "
            f"2. Root Cause "
            f"3. Raw Evidence (exact log lines verbatim in code block) "
            f"4. Remediation Steps Performed "
            f"5. Scripts Used "
            f"6. Follow-up Recommendations "
            f"Create the directory if it doesn't exist."
        )

        runbook_result = ""
        async with httpx.AsyncClient(timeout=600) as client:
            async with client.stream(
                "POST",
                f"{url}/investigate",
                json={"prompt": runbook_prompt, "thread_id": thread_id},
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json

                        try:
                            event = json.loads(line[6:])
                            if event.get("type") == "result":
                                runbook_result = event.get("data", {}).get("text", "")
                        except Exception:
                            pass

        if runbook_result:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    SLACK_ALERT_WEBHOOK_URL,
                    json={
                        "text": f":notebook: *[RUNBOOK SAVED] {alert_name}*\n\n{runbook_result[:2000]}\n\n_Saved to: `{runbook_path}`_"
                    },
                )

    except Exception as e:
        print(f"[webhook] IncidentFox trigger error: {e}")


@app.post("/webhook")
async def alertmanager_webhook(request: Request):
    body = await request.json()
    for alert in body.get("alerts", []):
        if alert["status"] != "firing":
            continue
        name = alert["labels"].get("alertname", "Unknown")
        instance = alert["labels"].get("instance", "unknown")
        summary = alert["annotations"].get("summary", "No summary")

        template = PROMPTS.get(name, DEFAULT_PROMPT)
        prompt = template.format(name=name, instance=instance, summary=summary)

        import time

        thread_id = f"alert-{name}-{int(time.time())}".replace(":", "-").replace(
            ".", "-"
        )

        slack_message = (
            f":rotating_light: *[FIRING] {name}*\n"
            f"Instance: `{instance}`\n"
            f"Summary: {summary}\n\n"
            f"<@U0AK04THCQ0> <@U0AK79BGX8D> — IncidentFox is investigating automatically..."
        )
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(SLACK_WEBHOOK_URL, json={"text": slack_message})

        import asyncio

        asyncio.create_task(
            _trigger_investigate(INCIDENTFOX_URL, prompt, thread_id, name)
        )

    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9095)
