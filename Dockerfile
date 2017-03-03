FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y python3-venv libpq-dev supervisor libpython3-dev \
                       git nginx npm nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    useradd --create-home --shell /bin/bash cesium

RUN python3 -m venv /cesium_env && \
    \
    bash -c "source /cesium_env/bin/activate && \
    pip install --upgrade pip && \
    pip install --upgrade pip"

ADD . /cesium
WORKDIR /cesium

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN bash -c "source /cesium_env/bin/activate && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    make paths && \
    make dependencies && \
    cp docker/cesium-docker.yaml . && \
    chown -R cesium.cesium /cesium_env && \
    chown -R cesium.cesium /cesium"

USER cesium

EXPOSE 5000

CMD bash -c "source /cesium_env/bin/activate && \
  (make log &) && \
  PYTHONPATH=. python -c \"from cesium_app.models import create_tables as c; c()\" && \
  make run"
