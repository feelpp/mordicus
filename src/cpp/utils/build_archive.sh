#!/bin/sh

set -xe

mkdir -p /tmp/mordicus
code="focal"
for distro in centos:8 debian:buster ubuntu:focal
do
  echo "FROM ${distro}\nENV DEBIAN_FRONTEND=noninteractive\nRUN apt-get -y update && apt-get -y install g++ cmake zip || yum install -y gcc-c++ cmake make zip" > /tmp/mordicus/Dockerfile
 
  docker build /tmp/mordicus -t mordicus_${distro}
  docker run --rm --volume `pwd`:/io mordicus_${distro} sh -c "cd /tmp && mkdir build && cd build && cmake -DBUILD_PYTHON=OFF -DCMAKE_INSTALL_PREFIX=~/.local /io 1>&2 && make install -j8 1>&2 && zip -r mordicus-${distro}.zip ~/.local 1>&2 && cat mordicus-${distro}.zip" > /tmp/mordicus/mordicus-${distro}.zip
done


