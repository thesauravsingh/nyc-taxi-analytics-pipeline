CREATE TABLE IF NOT EXISTS RAW_DB.NYC_TAXI.YELLOW_TRIPS (
    VendorID INT,
    tpep_pickup_datetime TIMESTAMP_NTZ,
    tpep_dropoff_datetime TIMESTAMP_NTZ,
    passenger_count NUMBER(38,0),
    trip_distance NUMBER(38, 2),
    RatecodeID NUMBER(38,0),
    store_and_fwd_flag VARCHAR(1),
    PULocationID NUMBER(38,0),
    DOLocationID NUMBER(38,0),
    payment_type NUMBER(38,0),
    fare_amount NUMBER(38, 2),
    extra NUMBER(38, 2),
    mta_tax NUMBER(38, 2),
    tip_amount NUMBER(38, 2),
    tolls_amount NUMBER(38, 2),
    improvement_surcharge NUMBER(38, 2),
    total_amount NUMBER(38, 2),
    congestion_surcharge NUMBER(38, 2),
    airport_fee NUMBER(38, 2)
);

CREATE TABLE IF NOT EXISTS RAW_DB.NYC_TAXI.TAXI_ZONES(
    location_id NUMBER(38,0),
    BOROUGH VARCHAR(100),
    zone VARCHAR(100),
    service_zone VARCHAR(20)
)

CREATE OR REPLACE FILE FORMAT my_parquet_format
    TYPE = 'PARQUET'
    COMPRESSION = 'SNAPPY';

CREATE OR REPLACE FILE FORMAT my_csv_format
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE; 

CREATE OR REPLACE STAGE RAW_DB.NYC_TAXI.TAXI_STAGE;