FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y curl build-essential software-properties-common && \
    curl -sL https://deb.nodesource.com/setup_7.x | bash - && \
    add-apt-repository ppa:jonathonf/python-3.6 && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y python3.6 python3.6-venv python3.6-dev \
                       libpq-dev supervisor \
                       git nginx nodejs postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    useradd --create-home --shell /bin/bash cesium

RUN python3.6 -m venv /cesium_env && \
    \
    bash -c "source /cesium_env/bin/activate && \
    pip install --upgrade pip && \
    pip install --upgrade pip"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ADD . /cesium
WORKDIR /cesium

RUN bash -c "\
    source /cesium_env/bin/activate && \
    make -C baselayer paths && \
    (make -C baselayer dependencies || make -C baselayer dependencies) && \
    make -C baselayer bundle && \
    rm -rf node_modules && \
    chown -R cesium.cesium /cesium_env && \
    chown -R cesium.cesium /cesium && \
    cp docker.yaml config.yaml"

USER cesium

EXPOSE 5000

CMD bash -c "source /cesium_env/bin/activate && \
             (make log &) && \
             make run_production"

