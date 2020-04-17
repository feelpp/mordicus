FROM debian:latest

RUN apt-get update && \
    apt-get install -y git python3 python3-pip libopenmpi-dev && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*

ENV BASICTOOLS_BUILD_CYTHON=False
ADD poc-1 /root/mordicus

RUN cd /root/mordicus && pip3 install .




 