FROM ubuntu:16.04

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y python3 python3-venv libpq-dev libhdf5-serial-dev \
                       libnetcdf-dev supervisor libpython3-dev supervisor \
                       nginx npm nodejs

RUN python3 -m venv /cesium_env

ADD . /cesium
WORKDIR /cesium
RUN bash -c "source /cesium_env/bin/activate && \
    pip install --upgrade pip && \
    pip install --upgrade pip && \
    export PIP_FIND_LINKS=http://wheels.scikit-image.org && \
    make paths && \
    make dependencies && \
    cp docker/cesium-docker.yaml . && \
    cp docker/* . && \
    ln -s /usr/bin/nodejs /usr/bin/node"

EXPOSE 5000

CMD bash -c "source /cesium_env/bin/activate && \
             supervisord -c conf/supervisord.conf"

