FROM ubuntu:16.04

ADD . /cesium
WORKDIR /cesium

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y python3 python3-venv libpq-dev libhdf5-serial-dev \
                       libnetcdf-dev supervisor libpython3-dev supervisor \
                       nginx npm nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    \
    python3 -m venv /cesium_env && \
    \
    bash -c "source /cesium_env/bin/activate && \
    pip install --upgrade pip && \
    pip install --upgrade pip && \
    export PIP_FIND_LINKS=http://wheels.scikit-image.org && \
    make paths && \
    make dependencies && \
    cp docker/cesium-docker.yaml . && \
    ln -s /usr/bin/nodejs /usr/bin/node"

EXPOSE 5000

CMD bash -c "source /cesium_env/bin/activate && \
  make log & \
  PYTHONPATH=. python -c \"from cesium_app.models import create_tables as c; c()\" && \
  supervisord -c conf/supervisord.conf"

