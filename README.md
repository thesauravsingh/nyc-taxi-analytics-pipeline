# NYC Taxi Analytics Pipeline

End-to-end ELT pipeline on the modern data stack: NYC TLC taxi trip data → Snowflake (raw) → dbt (staging → intermediate → marts, with SCD Type 2) → Airflow orchestration → Tableau Public.

**Status:** in progress — Phase 1 (Snowflake setup and raw ingestion).

## What's here

| Path | Contents |
|---|---|
| `PROJECT_1_DBT_SNOWFLAKE 2.md` | Build spec: phases, acceptance criteria, stack decisions |
| `NOTES.md` | Learning notes taken while building |
| `ingestion/load_taxi_data.py` | Loads monthly Parquet files into a Snowflake stage |
| `tables.sql` | Raw table definitions |
| `inspect_data.py`, `*_practice.ipynb` | Data exploration and practice |

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install snowflake-connector-python python-dotenv pandas pyarrow
cp .env.example .env   # fill in your Snowflake credentials
```

The practice notebooks (`pandas_practice.ipynb`, `sql_practice.ipynb`) also need Jupyter and DuckDB:

```bash
pip install jupyter duckdb
```

Trip data (`data/*.parquet`) is not committed. Download it from the [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) page into `data/`.
