mordicus_add_module(SciMeshReader SciMeshReader.cpp)
target_link_libraries(SciMeshReader PRIVATE SciMesh)
target_include_directories(SciMeshReader PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../common)
target_include_directories(SciMeshReader PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../../container/mesh/SciMesh)
