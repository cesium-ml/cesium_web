FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:fkrull/deadsnakes && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y python3.5 python3-venv libpq-dev libhdf5-serial-dev \
                       libnetcdf-dev supervisor libpython3-dev supervisor \
                       nginx npm nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    useradd --create-home --shell /bin/bash cesium

RUN python3.5 -m venv /cesium_env && \
    \
    bash -c "source /cesium_env/bin/activate && \
    pip install --upgrade pip && \
    pip install --upgrade pip"

ENV PIP_FIND_LINKS http://wheels.scikit-image.org
ADD . /cesium
WORKDIR /cesium

RUN bash -c "source /cesium_env/bin/activate && \
    make paths && \
    make dependencies && \
    cp docker/cesium-docker.yaml . && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    chown -R cesium.cesium /cesium_env && \
    chown -R cesium.cesium /cesium"

USER cesium

EXPOSE 5000

CMD bash -c "source /cesium_env/bin/activate && \
  (make log &) && \
  PYTHONPATH=. python -c \"from cesium_app.models import create_tables as c; c()\" && \
  make run"

