
macro(mordicus_add_module name sources)
  add_library (${name} SHARED ${sources})
  set_target_properties(${name} PROPERTIES PREFIX "")
  generate_export_header (${name})
  target_link_libraries (${name} PUBLIC mordicus)
  target_include_directories(${name} PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR};${CMAKE_CURRENT_BINARY_DIR}>"
    $<INSTALL_INTERFACE:include>)
  install(TARGETS ${name}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endmacro()

add_subdirectory (esigroup/io/SciMeshReader)
add_subdirectory (esigroup/container/mesh/SciMesh)
