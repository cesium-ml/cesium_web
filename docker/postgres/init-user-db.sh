#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  CREATE USER cesium;
  CREATE DATABASE cesium;
  GRANT ALL PRIVILEGES ON DATABASE cesium TO cesium;
EOSQL

cd /cesium
source /cesium_env/bin/activate && \
  PYTHONPATH=. python -c "from cesium_app.models import create_tables as c; c()"

