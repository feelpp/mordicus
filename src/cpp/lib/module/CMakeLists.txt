
macro(mordicus_add_module name sources)
  add_library (${name} MODULE ${sources})
  set_target_properties(${name} PROPERTIES PREFIX "")
  generate_export_header (${name})
  target_link_libraries (${name} PRIVATE mordicus)
  target_include_directories(${name} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
  target_include_directories(${name} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
  target_include_directories(${name} PRIVATE ${CMAKE_BINARY_DIR}/lib/src)
  target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR}/lib/src)
  install(TARGETS ${name}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endmacro()

add_subdirectory (esigroup/io/SciMeshReader)
add_subdirectory (esigroup/container/mesh/SciMesh)
