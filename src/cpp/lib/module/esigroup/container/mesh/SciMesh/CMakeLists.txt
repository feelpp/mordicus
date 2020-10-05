mordicus_add_module(SciMesh SciMesh.cpp)
target_include_directories(SciMesh PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../../common>")
