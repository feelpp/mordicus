mordicus_add_module(SciMesh SciMesh.cpp SciMesh.h ../../../common/SciStorage.hpp ../../../common/SciMordicus.hpp)
target_include_directories(SciMesh PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../../common>")
