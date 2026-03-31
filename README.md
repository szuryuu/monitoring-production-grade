# Monitoring Production Grade

A production-grade server monitoring stack with AI-powered automated incident response.

---

## Features

- **High-Performance Storage Engine**  
  VictoriaMetrics as long-term storage backend — up to 10x better compression than standard Prometheus, with fast query performance.

- **Decoupled Architecture**  
  Prometheus focuses solely on scraping and forwarding via `remote_write`. Heavy storage and querying offloaded to VictoriaMetrics.

- **Full Observability Stack**  
  Metrics (Prometheus + VictoriaMetrics), logs (Loki + Promtail), and visualization (Grafana) — all in one `docker compose up`.

- **AI-Powered Incident Response (IncidentFox)**  
  Automatic alert investigation, root cause analysis, and runbook generation — powered by Claude via IncidentFox. Zero manual trigger required.

- **Automated Alert Flow**  
  Prometheus → Alertmanager → Webhook Bridge → Slack notification + IncidentFox auto-investigation → runbook saved to disk.

---

## Architecture

![Architecture](https://raw.githubusercontent.com/szuryuu/monitoring-production-grade/main/docs/assets/monitoring-architecture2.png)

---

## Tech Stack

| Component           | Type          | Role                                                  |
| :------------------ | :------------ | :---------------------------------------------------- |
| **VictoriaMetrics** | Storage       | High-performance long-term TSDB                       |
| **Prometheus**      | Collector     | Stateless scraping agent + metric forwarder           |
| **Grafana**         | Visualization | Centralized dashboard                                 |
| **Loki**            | Log Storage   | Centralized log aggregation                           |
| **Promtail**        | Log Agent     | Scrapes container + syslog, ships to Loki             |
| **Alertmanager**    | Alerting      | Routes alerts to webhook bridge                       |
| **Webhook Bridge**  | Bridge        | Forwards alerts to Slack + triggers IncidentFox       |
| **IncidentFox**     | AI SRE Agent  | Auto-investigates alerts, remediates, writes runbooks |
| **Node Exporter**   | Exporter      | Host-level metrics (CPU, memory, disk)                |
| **Docker**          | Runtime       | Containerization                                      |
| **Terraform**       | IaC           | Infrastructure provisioning on Azure                  |

---

## Quick Start

### 1. Provision Infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Fill in your values
terraform init && terraform apply
```

### 2. SSH into VM and Setup Monitoring

```bash
cd ~/monitoring
cp .env.example .env
vi .env  # Fill in Slack tokens, Loki credentials, etc.

# Generate promtail config from template (substitutes env vars)
envsubst < promtail-config.yml.template > promtail-config.yml

docker compose up -d
```

### 3. Setup IncidentFox

```bash
cd ~
git clone https://github.com/incidentfox/incidentfox
cd incidentfox
cp .env.example .env
vi .env  # Fill in Slack tokens, AI provider keys, and monitoring URLs

# Required addition to .env:
# CONFIG_SERVICE_ADMIN_TOKEN=local-admin-token

# For docker remediation capability, add to docker-compose.yml sre-agent:
# group_add: ["999"]
# volumes:
#   - /var/run/docker.sock:/var/run/docker.sock:rw
#   - /usr/bin/docker:/usr/bin/docker:ro
#   - /home/adminuser/runbooks:/home/agent/runbooks:rw

make dev
```

### 4. Connect Networks

```bash
docker network create monitoring-incidentfox
docker network connect monitoring-incidentfox prometheus
docker network connect monitoring-incidentfox alertmanager
docker network connect monitoring-incidentfox alertmanager-webhook-bridge
docker network connect incidentfox_app_network alertmanager-webhook-bridge
```

---

## Environment Variables

See `monitoring/.env.example` for all required variables.

Key variables:

```
SLACK_INCOMING_WEBHOOK_URL=   # For alert notifications
SLACK_ALERT_WEBHOOK_URL=      # For investigation results (second webhook)
SLACK_BOT_USER_ID=            # IncidentFox bot user ID
INCIDENTFOX_URL=              # http://incidentfox-sre-agent:8000
LOKI_URL=                     # External Loki URL
LOKI_USERNAME=
LOKI_PASSWORD=
```

---

## IncidentFox Integration

Full documentation available at: **[szuryuu.dev/writing](https://szuryuu.dev/writing)**

Articles covering:

- Setup and installation guide
- Loki integration and testing
- CPU spike investigation
- Alertmanager integration (all approaches including failed ones)
- Full incident flow: detection → remediation → runbook
- Memory spike investigation (no docker permission case)
- Runbook generation guide
- Config corruption investigation (graceful failure case)
- Fully automated alert investigation via dual webhook

---

## License

MIT License — see [LICENSE](LICENSE) for details.
