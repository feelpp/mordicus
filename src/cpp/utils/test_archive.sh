#!/bin/sh

set -xe

cd /tmp/mordicus/
unzip -o mordicus-ubuntu:focal.zip
echo "cmake_minimum_required (VERSION 3.2)\nproject (test)\nfind_package (mordicus)\nadd_executable(test1 main.cpp)\ntarget_link_libraries(test1 mordicus::SciMesh)" > CMakeLists.txt
echo "#include <mordicus/modules/SciMesh.h>\nint main() { return 0; }" > main.cpp
cmake -Dmordicus_DIR=$PWD/root/.local/lib/cmake/mordicus . && make VERBOSE=1



