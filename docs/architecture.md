# Architecture

```mermaid
---
config:
  layout: dagre
  look: handDrawn
  theme: dark
---
flowchart LR
    User["User / Admin<br>Browser"]

    subgraph Server["Monitoring Server"]
        subgraph Network["Docker Network: monitoring (bridge)"]
            NodeExporter["Node Exporter<br>port 9100"]
            Prometheus["Prometheus<br>port 9090<br>(scrape agent only)"]
            VictoriaMetrics["Victoria Metrics<br>port 8428<br>(storage + query)"]
            Grafana["Grafana<br>port 3000"]
        end

        subgraph Volumes["Docker Volumes"]
            vV[("victoria_metrics_data")]
            vP[("prometheus_data")]
            vG[("grafana_data")]
        end

        CF["/monitoring/prometheus.yml"]
    end

    User -- "HTTP :3000" --> Grafana
    Prometheus -- "scrape :9100<br>every 15s" --> NodeExporter
    Prometheus -- "remote_write<br>/api/v1/write" --> VictoriaMetrics
    Grafana -- "query :8428" --> VictoriaMetrics
    VictoriaMetrics -- "metrics data" --> Grafana
    CF -- "mounted config" --> Prometheus
    Grafana ---> User
    VictoriaMetrics --- vV
    Prometheus --- vP
    Grafana --- vG
```

## Workflow

1. User opens browser and accesses Grafana on port 3000
2. Prometheus continuously scrapes Node Exporter every 15s to collect host metrics (CPU, memory, disk, network)
3. Prometheus remote_writes the collected metrics into VictoriaMetrics for persistent storage
4. Grafana sends a query to VictoriaMetrics on port 8428 when user opens a dashboard
5. VictoriaMetrics processes the query and returns the metrics data back to Grafana
6. Grafana renders the data as visualizations and serves the dashboard back to the user's browser

