<!--
# Monitoring Production Grade

A server monitoring implementation at the production level

---

## Features

-   **High-Performance Storage Engine**  
    Utilizes VictoriaMetrics as a long-term storage backend to achieve up to 10 times better compression than standard Prometheus, enabling metric storage for months with minimal RAM and disk usage.

-   **Unburdened Server (Decoupled Architecture)**  
    Heavy tasks are divided in two: Prometheus only focuses on being a data recording “courier,” then immediately sends it to the storage warehouse. So, the monitoring process will not consume CPU resources that should be used for your main application.

-   **Detailed System Monitoring**  
    Built-in hardening with **Azure Key Vault** for secret management (no hardcoded credentials), **Managed Identity** (RBAC) for secure resource access, and strict **Network Security Groups** to minimize attack surface.


-   **Low-Latency Query Performance**  
    Grafana retrieves data directly from VictoriaMetrics, which is designed for super-fast performance. The result? When you open the dashboard, the graphs appear instantly (no loading time), even with large amounts of data.
-->

## Architecture

![Architecture](https://raw.githubusercontent.com/szuryuu/monitoring-production-grade/main/docs/assets/monitoring-architecture.png)
*(See [Architecture Docs](./docs/architecture.md) for details)*

## Tech Stack

| Component | Type | Role in Architecture |
| :--- | :--- | :--- |
| **VictoriaMetrics** | Storage | High-performance Long-term Time Series Database (TSDB) |
| **Prometheus** | Collector | Stateless scraping agent & metric forwarder (via `remote_write`) |
| **Grafana** | Visualization | Centralized observability & data visualization dashboard |
| **Node Exporter** | Exporter | Hardware & OS-level metric collector |
| **Docker** | Runtime | Containerization & service isolation |
| **Terraform** | IaC | Infrastructure Provisioning & State Management |

## Summary

TBA


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

