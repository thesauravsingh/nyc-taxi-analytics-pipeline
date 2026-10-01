# Build Spec: Modern Data Stack — NYC Taxi Analytics Pipeline

> A production-style ELT pipeline demonstrating end-to-end analytics engineering skills using the modern data stack.

## Project Goal (One Sentence)

Build a dbt-on-Snowflake project that ingests raw NYC taxi data, transforms it through layered models (staging → intermediate → marts) with SCD Type 2 history, tests, and orchestration via Airflow, then visualizes business KPIs in Tableau Public.

## Why This Project Exists

The hiring market for Analytics Engineers and Data Engineers in 2026 expects fluency with the modern data stack (dbt + Snowflake + Airflow + a BI tool). This project demonstrates the full lifecycle: raw ingestion → dimensional modeling → tested transformations → orchestrated pipelines → consumer-facing dashboards. It also includes deliberate engineering choices (SCD Type 2, custom tests, exposures) that signal depth beyond tutorial-level work.

## What Done Looks Like

- [ ] GitHub repo with clean structure, README, and architecture diagram
- [ ] Snowflake account with loaded raw NYC taxi data (one year, partitioned by month)
- [ ] dbt project with at least 3 staging models, 2 intermediate models, 1 fact + 3 dimension marts
- [ ] At least one **SCD Type 2** dimension (taxi zone with location attribute changes)
- [ ] At least 10 dbt tests (mix of generic and custom singular tests)
- [ ] dbt docs site generated and screenshot in README
- [ ] Airflow DAG (using astro CLI locally) that runs the full pipeline end-to-end
- [ ] Tableau Public dashboard with 3-4 charts answering real business questions
- [ ] README with: architecture diagram, setup instructions, screenshots, "what I learned" section

## Tech Stack & Why

| Tool | Why this choice |
|---|---|
| **Snowflake** (30-day free trial) | Industry-standard cloud DW, free tier gives $400 credit (plenty for this project) |
| **dbt-core** (not Cloud) | Cloud version is free but limited; dbt-core demonstrates full setup skill |
| **dbt-snowflake** adapter | Matches Snowflake choice |
| **Airflow** via `astro` CLI | Easiest local Airflow setup; Astronomer is the gold standard for Airflow in industry |
| **Tableau Public** (free) | Free, hosted, shareable link in resume |
| **NYC Taxi data** | Public, well-documented, 100M+ rows per year (real scale), interesting business questions |
| **GitHub** | Where the work lives |

## Dataset: NYC Yellow Taxi Trip Records

**Source:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

**What to load:**
- **Trip records:** 12 monthly Parquet files for 2024 (~3M rows/month, ~36M total) — this gives you real scale
- **Taxi zone lookup:** small CSV with zone_id, borough, zone_name
- **Optional weather data:** NOAA daily NYC weather (adds a fun cross-domain join)

**Why this dataset:**
- Public, no auth needed
- Real scale (~36M rows)
- Has timestamps for time-series analysis
- Has spatial dimensions (pickup/dropoff zones) for SCD demonstration
- Has business questions you can actually answer (revenue trends, tip patterns, busiest zones)

## Project Structure

```
nyc-taxi-analytics/
├── README.md                          # Main project README
├── ARCHITECTURE.md                    # Architecture diagram + decisions
├── .gitignore                         # Standard Python + dbt gitignore
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # For pgvector if you cross-use it; optional here
│
├── ingestion/                         # Snowflake loading scripts
│   ├── load_taxi_data.py             # Downloads + COPY INTOs raw data
│   ├── load_zones.py                  # Loads taxi zone lookup
│   └── snowflake_setup.sql            # Creates RAW database/schema/warehouse
│
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml.example           # Template, real one in ~/.dbt/
│   ├── packages.yml                   # dbt_utils, dbt_expectations
│   ├── models/
│   │   ├── staging/
│   │   │   ├── _sources.yml          # Raw source declarations
│   │   │   ├── _staging.yml          # Tests + docs for staging
│   │   │   ├── stg_taxi_trips.sql
│   │   │   ├── stg_taxi_zones.sql
│   │   │   └── stg_weather.sql       # Optional
│   │   ├── intermediate/
│   │   │   ├── int_trips_enriched.sql      # Trips joined with zones + weather
│   │   │   └── int_trips_aggregated.sql    # Hourly aggregates
│   │   ├── marts/
│   │   │   ├── _marts.yml
│   │   │   ├── dim_date.sql                 # Date dimension
│   │   │   ├── dim_zone.sql                 # SCD Type 2 zone dimension
│   │   │   ├── dim_payment_type.sql         # Simple dim
│   │   │   └── fct_trips.sql                # Fact table
│   │   └── snapshots/
│   │       └── zone_snapshot.sql            # SCD Type 2 snapshot
│   ├── tests/
│   │   ├── assert_positive_fare.sql         # Custom singular test
│   │   ├── assert_dropoff_after_pickup.sql  # Custom singular test
│   │   └── assert_no_orphan_trips.sql       # Referential test
│   ├── macros/
│   │   └── generate_schema_name.sql         # Override default schema
│   └── seeds/
│       └── (small reference CSVs if needed)
│
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dags/
│       └── taxi_analytics_dag.py
│
├── dashboards/
│   ├── tableau_link.md                # Link to published Tableau dashboard
│   └── screenshots/
│       ├── dashboard_overview.png
│       └── dbt_docs_lineage.png
│
└── docs/
    ├── architecture.png               # Created in Excalidraw
    └── data_model.png                 # ERD of fact + dims
```

## Build Order (Do These In Order)

### Phase 1: Foundation (Day 1-2, ~3 hours)

**1.1 Snowflake setup**
- Sign up for Snowflake 30-day trial: https://signup.snowflake.com/
- Choose Enterprise edition, AWS region closest to you
- Save: account identifier, username, password — you'll need these for dbt
- In Snowflake UI, run `ingestion/snowflake_setup.sql` to create:
  - `RAW_DB` database
  - `RAW_DB.NYC_TAXI` schema
  - `ANALYTICS_DB` database (for dbt outputs)
  - `TRANSFORM_WH` warehouse (XS size — cheap)
  - `DBT_ROLE` role with appropriate grants

**1.2 Local dbt setup**
- Python 3.11 venv: `python -m venv venv && source venv/bin/activate`
- `pip install dbt-core dbt-snowflake`
- `dbt init nyc_taxi_analytics` to scaffold project
- Configure `~/.dbt/profiles.yml` with Snowflake credentials
- `dbt debug` — must pass before proceeding

**1.3 GitHub repo**
- Create public repo `nyc-taxi-analytics`
- Add `.gitignore` for Python + dbt
- **Never commit profiles.yml** — keep a `.example` template only
- Initial commit with empty structure

**Acceptance criteria for Phase 1:**
- [ ] `dbt debug` returns all green
- [ ] You can query `SELECT 1` from Snowflake via dbt
- [ ] GitHub repo exists and is empty-but-structured

### Phase 2: Raw Data Ingestion (Day 2-3, ~3 hours)

**2.1 Write the ingestion script**
- `ingestion/load_taxi_data.py` should:
  - Download 12 monthly Parquet files from NYC TLC website (URLs follow predictable pattern)
  - Use `snowflake-connector-python` to upload to Snowflake stage
  - Run `COPY INTO RAW_DB.NYC_TAXI.YELLOW_TRIPS` to load
  - Log row counts per month
- Add error handling for partial loads (idempotency: skip months already loaded)

**2.2 Load zone lookup**
- Download `taxi_zone_lookup.csv` from same NYC TLC page
- Load to `RAW_DB.NYC_TAXI.TAXI_ZONES`

**2.3 Verify**
- Total trip rows should be ~30-40M
- Zone count should be 265
- Query a sample to make sure timestamps parsed correctly

**Acceptance criteria for Phase 2:**
- [ ] `SELECT COUNT(*) FROM RAW_DB.NYC_TAXI.YELLOW_TRIPS` returns 30M+
- [ ] `SELECT COUNT(*) FROM RAW_DB.NYC_TAXI.TAXI_ZONES` returns 265
- [ ] Ingestion script is idempotent (re-running doesn't duplicate)

### Phase 3: dbt Staging Layer (Day 3-4, ~2 hours)

Staging = 1:1 source-to-model with light cleaning (renaming, casting, null handling). NO joins.

**3.1 Sources declaration** — `models/staging/_sources.yml`
- Declare `nyc_taxi` source pointing to `RAW_DB.NYC_TAXI`
- Add `freshness` blocks (warn after 7 days, error after 14)

**3.2 Staging models**
- `stg_taxi_trips.sql`: Clean trip records — rename columns to snake_case, cast timestamps, filter obvious garbage (negative fares, zero-distance trips with non-zero fare)
- `stg_taxi_zones.sql`: Clean zone lookup
- Each staging model materialized as `view` (default)

**3.3 Staging tests** — `models/staging/_staging.yml`
- `not_null` on primary keys
- `unique` on trip identifier (if available, or create surrogate key)
- `accepted_values` on payment_type

**Acceptance criteria for Phase 3:**
- [ ] `dbt run --select staging` succeeds
- [ ] `dbt test --select staging` passes
- [ ] Row counts in staging match raw (no accidental row loss)

### Phase 4: Intermediate Layer (Day 4, ~2 hours)

Intermediate = business logic, joins, partial aggregations. Stuff that's reused across marts.

**4.1 Intermediate models**
- `int_trips_enriched.sql`: Join trips with zones (pickup + dropoff), enrich with derived columns (trip_duration_minutes, fare_per_mile, is_weekend, hour_of_day, day_of_week)
- `int_trips_aggregated.sql`: Hourly aggregates by zone (trip_count, total_revenue, avg_tip_pct)

**4.2 Materialization strategy**
- `int_trips_enriched` as `table` (large, used downstream often)
- `int_trips_aggregated` as `view` (small, derived)

**Acceptance criteria for Phase 4:**
- [ ] `dbt run --select intermediate` succeeds
- [ ] Sample query to `int_trips_enriched` shows pickup + dropoff zone names

### Phase 5: Marts Layer + SCD Type 2 (Day 5-6, ~4 hours)

This is the part recruiters care about most.

**5.1 dbt snapshot for SCD Type 2** — `snapshots/zone_snapshot.sql`
- Create a snapshot on `taxi_zones` with `strategy='timestamp'` (or `check` if you simulate changes manually)
- Simulate a change: manually update a borough name for one zone, re-run snapshot, see Type 2 history
- This is the **#1 thing interviewers will probe on** for this project

**5.2 Dimension marts**
- `dim_date.sql`: Generate date dimension for 2024 (use `dbt_utils.date_spine`)
- `dim_zone.sql`: Built FROM the snapshot — should have `valid_from`, `valid_to`, `is_current` columns
- `dim_payment_type.sql`: Simple mapping

**5.3 Fact mart**
- `fct_trips.sql`: Trip-level fact table with FKs to dim_date, dim_zone (pickup), dim_zone (dropoff), dim_payment_type
- Materialized as `table` with `cluster_by=['pickup_date']` for query performance

**5.4 Tests on marts**
- Referential integrity tests (dbt_utils `relationships` test)
- Custom singular tests:
  - `assert_positive_fare.sql` (fare_amount > 0)
  - `assert_dropoff_after_pickup.sql` (dropoff_timestamp > pickup_timestamp)
  - `assert_no_orphan_trips.sql` (every trip has a valid pickup_zone_key in dim_zone)

**Acceptance criteria for Phase 5:**
- [ ] `dbt run` succeeds end-to-end
- [ ] `dbt test` passes (10+ tests passing)
- [ ] SCD Type 2 zone has at least 2 versions of one zone (your manual change is captured)

### Phase 6: dbt Docs + Exposures (Day 6, ~1.5 hours)

**6.1 Documentation**
- Add `description` to every model in `.yml` files
- Add column-level docs for at least the fact table
- `dbt docs generate && dbt docs serve` — should produce a lineage graph

**6.2 Exposures**
- Add an `exposure` definition pointing to the Tableau dashboard (even before you build it — placeholder URL is fine)
- This is a subtle but real signal of analytics engineering maturity

**6.3 Screenshot**
- Take a screenshot of the dbt docs lineage graph showing your DAG
- Save to `docs/dbt_docs_lineage.png`

### Phase 7: Airflow Orchestration (Day 7, ~3 hours)

**7.1 Setup astro CLI**
- Install: https://docs.astronomer.io/astro/cli/install-cli
- `astro dev init` in the `airflow/` directory
- This scaffolds a local Airflow + Docker setup

**7.2 Build the DAG** — `dags/taxi_analytics_dag.py`

DAG structure:
```
start
  ├─ check_source_freshness (dbt source freshness)
  ├─ run_staging (dbt run --select staging)
  ├─ run_intermediate (dbt run --select intermediate)
  ├─ snapshot_zones (dbt snapshot)
  ├─ run_marts (dbt run --select marts)
  ├─ test_models (dbt test)
  └─ end
```

- Schedule: `@daily`
- Use **`dbt-cosmos`** package (turns dbt project into Airflow tasks automatically — way better than BashOperator)
- Or use BashOperator for simplicity if cosmos is overkill
- Add **SLA**: each task should finish in <10 minutes (this is just for demo, not real SLA)
- Add **on_failure_callback** that logs to a sink (just print is fine for v1)

**7.3 Run locally**
- `astro dev start`
- Open `http://localhost:8080`, trigger the DAG manually
- Watch it run end-to-end
- Screenshot the successful DAG run for README

**Acceptance criteria for Phase 7:**
- [ ] Full DAG runs successfully end-to-end locally
- [ ] Retries configured (3 retries with exponential backoff)
- [ ] Screenshot in README

### Phase 8: Tableau Dashboard (Day 7-8, ~2 hours)

**8.1 Connect Tableau Public to Snowflake**
- Tableau Public has a free Snowflake connector
- Connect to `ANALYTICS_DB.PUBLIC.FCT_TRIPS` + dimensions

**8.2 Build 4 charts**
- Chart 1: Monthly revenue trend with weather overlay
- Chart 2: Top 10 pickup zones by trip volume (map if you can)
- Chart 3: Average tip percentage by payment type
- Chart 4: Hourly demand heatmap (day-of-week × hour)

**8.3 Publish**
- Publish to Tableau Public (free)
- Get the public URL
- Embed screenshot in README, link to live dashboard

### Phase 9: Documentation & Polish (Day 8-9, ~3 hours)

**9.1 Architecture diagram**
- Use Excalidraw (excalidraw.com) — free, no signup
- Draw: Raw Sources → Snowflake Raw → dbt Staging → Intermediate → Snapshots → Marts → Tableau
- Show Airflow orchestrating the dbt steps
- Export as PNG to `docs/architecture.png`

**9.2 Final README**
- See README template section below

**9.3 Pin to GitHub profile**
- Settings → Pinned repos → pin this one

## README Template — Use This Structure

```markdown
# NYC Taxi Analytics — Modern Data Stack Pipeline

End-to-end ELT pipeline transforming 30M+ NYC taxi trip records into trusted, tested, and visualized business metrics using dbt, Snowflake, Airflow, and Tableau.

[![dbt Version](https://img.shields.io/badge/dbt-1.7+-blue)](https://docs.getdbt.com/)
[![Snowflake](https://img.shields.io/badge/Snowflake-Cloud_DW-29B5E8)](https://www.snowflake.com/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8+-017CEE)](https://airflow.apache.org/)

## 📊 Live Dashboard
[View on Tableau Public →](your-tableau-url-here)

![Dashboard Preview](dashboards/screenshots/dashboard_overview.png)

## 🏗️ Architecture

![Architecture](docs/architecture.png)

**Data flow:**
1. Python ingestion script downloads NYC TLC monthly Parquet files → Snowflake `RAW_DB`
2. dbt transforms raw → staging → intermediate → marts (fact + dims with SCD Type 2)
3. Airflow (via Astronomer) orchestrates daily runs with tests, freshness checks, and snapshots
4. Tableau Public consumes the `fct_trips` mart for business dashboards

## 🎯 What This Demonstrates

- **Dimensional modeling**: Star schema with 1 fact + 3 dimensions
- **SCD Type 2**: Historical tracking of taxi zone changes via dbt snapshots
- **Data quality**: 12+ tests including custom singular tests for business logic
- **Orchestration**: Airflow DAG with retries, SLAs, and dbt-cosmos integration
- **Documentation**: dbt docs site with lineage, descriptions, and exposures
- **Self-serve BI**: Published Tableau dashboard answering real business questions

## 🛠️ Tech Stack
- **Snowflake** — Cloud data warehouse
- **dbt-core** — Transformation layer with tests, docs, snapshots
- **Apache Airflow** (Astronomer astro CLI) — Orchestration
- **Tableau Public** — Visualization
- **Python** — Ingestion scripts

## 📁 Repository Structure
[paste tree output here]

## 🚀 Setup Instructions
[step-by-step from Phase 1 above]

## 📈 dbt Lineage
![dbt Docs](dashboards/screenshots/dbt_docs_lineage.png)

## 💡 Key Design Decisions

**Why SCD Type 2 on zones?**
Taxi zones change over time (borough re-classifications, zone splits). SCD Type 2 preserves historical accuracy — a trip from 2022 is attributed to the zone as it existed then, not today.

**Why dbt-cosmos for Airflow?**
[Your reasoning here once you decide]

**Why XS warehouse?**
Cost optimization. 30M rows fits comfortably in XS for this workload; auto-suspend after 60 seconds keeps credit burn negligible.

## 📚 What I Learned
[Fill in honestly after building — interviewers love this section]

## 🔮 Future Improvements
- [ ] CI/CD with GitHub Actions running dbt tests on PRs
- [ ] Add streaming layer with Snowpipe
- [ ] Implement freshness SLAs that page on failure
```

## Common Pitfalls (Avoid These)

1. **Snowflake credit burn** — Use XS warehouse, set `auto_suspend=60`. Don't leave queries running overnight.
2. **profiles.yml in git** — `.gitignore` it. Use `profiles.yml.example` as template.
3. **Loading all 12 months at once** — Start with 1 month for development, scale up only when models work.
4. **Skipping tests** — "I'll add tests later" → you won't. Add tests as you build each model.
5. **Over-engineering ingestion** — A simple Python script is fine. Don't build a Kafka pipeline for static files.
6. **Trying to use dbt Cloud** — Stick with dbt-core. Cloud version hides skills you want to demonstrate.

## Interview Defense Notes (Be Ready For These)

**Q: "Walk me through the architecture."**
*A: 90-second pitch covering source → ingestion → transformation → orchestration → consumption. Mention scale (30M rows), key technical choice (SCD Type 2), and outcome (Tableau dashboard).*

**Q: "Why dbt and not just stored procs?"**
*A: Version control, testing framework, lineage docs, modular composability, dev/prod environment separation. Stored procs give you none of those.*

**Q: "What's SCD Type 2 and why did you use it?"**
*A: Type 2 preserves history by adding new rows with valid_from/valid_to columns rather than updating in place. Used it on zones because attributing historical trips to current zone definitions would be analytically wrong.*

**Q: "How would this scale to 10B rows?"**
*A: (a) Incremental materializations instead of full refresh, (b) clustering keys on fact table, (c) move heavy aggregations to scheduled rollups, (d) consider Iceberg tables for cheaper storage.*

**Q: "What went wrong while building this?"**
*A: Have a real answer. Maybe: "I underestimated how much data quality work staging requires — about 3% of rows had impossible values (negative distances, dropoffs before pickups). Added filters in staging and singular tests in marts."*

## Budget Estimate

- Snowflake: $0 (free trial covers it 10x over)
- Tableau Public: $0
- Airflow (local): $0
- GitHub: $0
- **Total: $0** — actually zero

## Timeline Reality Check

- **Aggressive (full-time-equivalent on weekends):** 5-7 days
- **Realistic (10-12 hours/week part-time):** 2-3 weeks
- **Padded for life:** 4 weeks

Aim for 2 weeks. If you hit 3, that's still excellent.

---

**Next:** Build this with Claude Code. Hand it this README and ask it to start at Phase 1. Iterate phase-by-phase, don't ask Claude Code to build everything at once.
