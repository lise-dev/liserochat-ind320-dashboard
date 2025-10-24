CREATE KEYSPACE IF NOT EXISTS elhub
  WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE elhub;
CREATE TABLE IF NOT EXISTS production_2021 (
  price_area text,
  production_group text,
  start_time timestamp,
  quantity_kwh double,
  PRIMARY KEY ((price_area), start_time, production_group)
) WITH CLUSTERING ORDER BY (start_time ASC, production_group ASC);
