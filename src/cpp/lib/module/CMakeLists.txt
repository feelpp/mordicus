
macro(mordicus_add_module name)
  option(MORDICUS_MODULE_ENABLE_${name} "Enable module ${name}" ON)
  if (MORDICUS_MODULE_ENABLE_${name})
    set (sources ${ARGN})
    add_library (${name} SHARED ${sources})
    set_target_properties(${name} PROPERTIES PREFIX "")
    generate_export_header (${name})
    string(TOLOWER ${name} name_lower)
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${name_lower}_export.h DESTINATION include/mordicus/modules)
    target_link_libraries (${name} PUBLIC mordicus)
    target_include_directories(${name} PUBLIC
      "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR};${CMAKE_CURRENT_BINARY_DIR}>"
      $<INSTALL_INTERFACE:include>)

    install(TARGETS ${name}
      EXPORT ${name}-targets
      LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
      RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

    foreach(source ${sources})
      if ("${source}" MATCHES ".*\.h$|.*\.hpp$")
        # TODO: keep directory structure
        install(FILES ${source} DESTINATION include/mordicus/modules)
      endif ()
    endforeach ()
    
    install(EXPORT ${name}-targets
          FILE ${name}-targets.cmake
          NAMESPACE mordicus::
          DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mordicus)
  endif ()
endmacro()

add_subdirectory (esigroup/io/SciMeshReader)
add_subdirectory (esigroup/container/mesh/SciMesh)
