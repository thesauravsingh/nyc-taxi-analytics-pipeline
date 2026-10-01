# Learning Notes — NYC Taxi Analytics Pipeline

Running notes as I build this project. Concepts in my own words, for interview prep and future reference.

---

## Phase 1 — Foundation (Snowflake + dbt + GitHub)

### The big idea: ELT, not ETL
- **E**xtract → pull raw data from source (NYC TLC Parquet files)
- **L**oad → dump it into the warehouse **as-is**, untouched (`RAW_DB`)
- **T**ransform → clean/reshape it **inside** the warehouse with SQL (dbt's job)
- Old way was ET**L** (transform before loading on a separate server). Modern stack flips it because cloud warehouses are cheap + fast: keep a pristine raw copy, do all shaping in version-controlled, testable SQL.
- In this project: **Snowflake = the "L" destination and the "T" engine; dbt = the "T" logic.**

### Snowflake's defining trait: compute and storage are decoupled
- **Database** = where data lives (storage). Cheap, always on. Holds schemas → tables.
- **Warehouse** = the compute that runs queries. **The only thing that meaningfully costs money**, and only while actively running a query.
- vs **Redshift**: classic Redshift couples compute+storage in one cluster. Snowflake fully decouples — a warehouse is ephemeral, auto-suspends, and **many warehouses can point at the same storage** with no copies. (This decoupling + auto-suspend is the headline "Snowflake vs Redshift" interview answer.)

### Object hierarchy (nests like folders)
```
Account
├── Warehouse   TRANSFORM_WH      ← compute (the meter)
├── Database    RAW_DB            ← raw loaded data
│   └── Schema  NYC_TAXI          ← holds YELLOW_TRIPS, TAXI_ZONES (Phase 2)
├── Database    ANALYTICS_DB      ← dbt writes its models here
└── Role        DBT_ROLE          ← a named bag of permissions
```
- **Two databases on purpose:** raw stays pristine in one; dbt outputs land in another. Blast-radius protection + clarity ("RAW = source of truth, ANALYTICS = derived"). Maturity signal.
- Every `CREATE DATABASE` auto-creates two schemas: `PUBLIC` (empty default) and `INFORMATION_SCHEMA` (read-only metadata).

### Warehouse cost knobs (= the budget guardrails)
| Knob | Value | Why |
|---|---|---|
| `WAREHOUSE_SIZE` | `'XSMALL'` | smallest/cheapest; 3 months of data fits fine |
| `AUTO_SUSPEND` | `60` | stop paying ~60s after a query ends |
| `AUTO_RESUME` | `TRUE` | wakes automatically on next query |
| `INITIALLY_SUSPENDED` | `TRUE` | creating it doesn't start the meter |
- A stray warehouse with a long `AUTO_SUSPEND` (e.g. default `COMPUTE_WH` = 600s) is how people accidentally burn trial credits.
- **Habit:** after creating something, verify it (`SHOW WAREHOUSES`) — don't assume.

### Roles, privileges, grants (least privilege)
- A **role** is not a person — it's a **named bag of permissions**. Users/tools "use" a role.
- **Principle: never let an automated tool run as god (ACCOUNTADMIN).** Make a dedicated `DBT_ROLE` that can do exactly what dbt needs and nothing more. If creds leak, damage is bounded.
- **Privilege = `<verb>` ON `<object>`.** Granted with `GRANT <priv> ON <object> TO ROLE <role>;`

What dbt needs (the interview answer):
1. `USAGE` on warehouse `TRANSFORM_WH` — run queries (compute)
2. `USAGE` on `RAW_DB` + `USAGE` on schema `NYC_TAXI` + `SELECT` on its tables — read raw
3. `USAGE` + `CREATE SCHEMA` on `ANALYTICS_DB` — write models

Two ideas that matter more than the privilege list:
- **`USAGE` is the "key to the container"** — appears at warehouse, database, AND schema level. To read a table you need the whole chain: `USAGE` on DB → `USAGE` on schema → `SELECT` on table. **Privileges do NOT inherit downward.** (Missing schema `USAGE` = baffling "object does not exist or not authorized" error.)
- **`OWNERSHIP` is special** — every object has exactly one owning role that can do anything to it. When `DBT_ROLE` creates a schema/table, it **owns** it automatically — so we don't grant `CREATE TABLE`; ownership cascades from `CREATE SCHEMA`.

Privilege tiers (the ones I need in **bold**):
- Account/global: `CREATE WAREHOUSE/DATABASE/ROLE/USER`, `MANAGE GRANTS`, `MONITOR`
- Warehouse: **`USAGE`**, `OPERATE`, `MODIFY`, `MONITOR`
- Database: **`USAGE`**, **`CREATE SCHEMA`**, `MODIFY`
- Schema: **`USAGE`**, `CREATE TABLE/VIEW/STAGE`
- Table/view: **`SELECT`**, `INSERT`, `UPDATE`, `DELETE`

- **FUTURE grants:** privileges don't auto-cover objects created later. Use `GRANT SELECT ON FUTURE TABLES IN SCHEMA ... ` so tables loaded in Phase 2 are covered. (`ON ALL TABLES` covers existing-only.)
- **Role hierarchy:** roles can be granted to other roles, forming a tree (`ACCOUNTADMIN` at top inherits everything). Keeping ours flat for now.

### Idempotency: `OR REPLACE` vs `IF NOT EXISTS`
- **`OR REPLACE` = drop and rebuild.** Fine for **stateless** objects (a warehouse holds no data). **Reckless for stateful** ones — `CREATE OR REPLACE DATABASE RAW_DB` on a re-run silently DROPS all loaded data.
- **`IF NOT EXISTS` = create only if missing, leave existing untouched.** Use for databases, schemas, roles.
- **Rule of thumb: `OR REPLACE` for stateless, `IF NOT EXISTS` for stateful.**
- A setup script should be safely **re-runnable** (idempotent).

### Account / connection facts (mine)
- Account identifier form dbt wants: **`<ORG>-<ACCOUNT>`** (hyphenated), e.g. `ABCDEFG-XY12345`. (My real value lives in the gitignored `credentials.local.md`.)
- Auth: signed up with **`authenticator = externalbrowser`** (SSO/browser), **no password**. So dbt `profiles.yml` will use `authenticator: externalbrowser` and omit the password — a browser tab pops up to log in.
- Snowflake names are case-insensitive, stored UPPERCASE unless double-quoted. Convention: write roles/warehouses/databases UPPERCASE.

### Security
- Connection details (account, user) and `profiles.yml` stay **local, never in git**. Keep a `.example` template only.
