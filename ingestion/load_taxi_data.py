import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_ACCOUNT=os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER=os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_WAREHOUSE=os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE=os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA=os.getenv('SNOWFLAKE_SCHEMA')
SNOWFLAKE_ROLE=os.getenv('SNOWFLAKE_ROLE')
SNOWFLAKE_PASSWORD=os.getenv('SNOWFLAKE_PASSWORD')

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA,
    role=SNOWFLAKE_ROLE,
    password=SNOWFLAKE_PASSWORD,
)

cur = conn.cursor()


cur.execute("SELECT CURRENT_VERSION(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
print(cur.fetchone())


cur.execute("PUT file:///Users/sauravsingh/Documents/Projects/nyc-taxi-analytics-pipeline/data/yellow_tripdata_2024-01.parquet @RAW_DB.NYC_TAXI.TAXI_STAGE/trips/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE");
cur.execute("PUT file:///Users/sauravsingh/Documents/Projects/nyc-taxi-analytics-pipeline/data/yellow_tripdata_2024-02.parquet @RAW_DB.NYC_TAXI.TAXI_STAGE/trips/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE");
cur.execute("PUT file:///Users/sauravsingh/Documents/Projects/nyc-taxi-analytics-pipeline/data/yellow_tripdata_2024-03.parquet @RAW_DB.NYC_TAXI.TAXI_STAGE/trips/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE");

cur.execute("COPY INTO RAW_DB.NYC_TAXI.YELLOW_TRIPS FROM @RAW_DB.NYC_TAXI.TAXI_STAGE/trips/ FILE_FORMAT = (FORMAT_NAME='my_parquet_format') MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE")
print(cur.fetchall())
print(cur.execute("SELECT COUNT(*) FROM RAW_DB.NYC_TAXI.YELLOW_TRIPS").fetchone())