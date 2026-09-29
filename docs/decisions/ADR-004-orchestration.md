# ADR-004: Orchestration Strategy (Apache Airflow vs Cron / Cloud Scheduler)

## Status
**Accepted**

## Context
The end-to-end data platform comprises multiple inter-dependent stages: source file validation, raw loading, audit logging, multi-layered dbt execution, data quality test suites, and downstream analytical reconciliation. A pipeline failure in one step must immediately halt downstream stages and trigger alerts, while providing full run history and retries.

## Decision
Adopt **Apache Airflow** containerized via Docker Compose to manage task dependency graphs, retries, failure alerting, and pipeline observability.

## Alternatives Considered
* **Linux Cron Jobs / Shell Scripts**:
  * *Rejected*: Zero task dependency management; no centralized UI for logs and execution history; difficult to coordinate failures; no backfill or retry logic.
* **Prefect / Dagster**:
  * *Considered*: Modern orchestrators with strong Python typing, but Apache Airflow remains the enterprise industry standard with broader corporate adoption and rich ecosystem support.
* **dbt Cloud Scheduler**:
  * *Rejected*: Can orchestrate dbt jobs, but cannot trigger external Python extraction scripts, checksum validations, or custom database reconciliation tasks outside the dbt scope.

## Tradeoffs & Consequences
* **Positive**: Full pipeline DAG topology visualization; automatic exponential retries on transient network hiccups; clear task separation.
* **Positive**: Strict rule enforced: Airflow orchestrates tasks via CLI and Operators; it does NOT execute heavy data transformations inside worker memory.
* **Tradeoff**: Airflow introduces operational complexity (Postgres metadata database, Webserver, Scheduler) compared to a single shell script. This is mitigated through our streamlined `docker-compose.yml` local container setup.
