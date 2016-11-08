#!/usr/bin/env bash

id -u postgres

if [[ $? == 0 ]]; then
    echo "Configuring Linux postgres"
    sudo -u postgres psql -c 'CREATE DATABASE cesium;'
    sudo -u postgres psql -c 'CREATE DATABASE cesium_test;'
    sudo -u postgres psql -c 'CREATE USER cesium;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
    sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE cesium_test to cesium;'
else
    echo "Configuring OSX postgres"
    createdb -w cesium
    createdb -w cesium_test
    createuser cesium
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium to cesium;'
    psql -U cesium -c 'GRANT ALL PRIVILEGES ON DATABASE cesium_test to cesium;'
fi

python -c  'from cesium_app.models import create_tables; create_tables()'
#python -c 'drop_tables()'
#python -c 'create_tables()'