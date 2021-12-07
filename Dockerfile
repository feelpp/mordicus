# -*- mode: Dockerfile -*-

FROM ghcr.io/feelpp/feelpp-mor-dev:latest

USER root
COPY . /root
RUN ls -lrtR /root

RUN dpkg -i /root/*.deb && rm /root/*.deb
USER feelpp