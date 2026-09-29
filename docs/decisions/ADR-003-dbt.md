# ADR-003: Transformation Layer Architecture (dbt Core vs Python Pandas ETL)

## Status
**Accepted**

## Context
Data transformations can either be executed in-memory via Python data processing scripts (e.g. Pandas, Polars, PySpark) before warehouse loading (ETL), or pushed down directly into the analytical data warehouse using SQL modeling frameworks (ELT).

## Decision
Use **dbt Core (Data Build Tool)** as the dedicated transformation engine operating on the warehouse, dividing models into three strict layers:
1. `staging/`: 1:1 view wrappers cleaning and casting raw tables.
2. `intermediate/`: Ephemeral or view models enriching entities (order aggregates, delivery calculations).
3. `marts/`: Business-facing physical tables serving dimensional facts and dimensions.

## Alternatives Considered
* **Python Pandas In-Memory ETL**:
  * *Rejected*: Loads millions of records into Python heap memory; lacks automated dependency graph resolution (DAGs); lacks automated documentation generation; changes are opaque to SQL-native data analysts; violates ELT separation of concerns.
* **Stored Procedures / Native SQL Scripts**:
  * *Rejected*: Difficult to version control; lacks automated data testing; zero lineage tracing; vendor lock-in.

## Tradeoffs & Consequences
* **Positive**: Full version-controlled software engineering lifecycle applied to data (CI testing, lineage graphs, automatic documentation).
* **Positive**: Leverage warehouse compute engine directly (MPP query planning) rather than maintaining separate compute workers for transformations.
* **Positive**: 104 data tests execute automatically as part of the build pipeline.
* **Tradeoff**: Requires team familiarity with Jinja templating and dbt project structure.
