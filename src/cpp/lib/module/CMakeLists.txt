
macro(mordicus_add_module name)
  string(TOUPPER ${name} name_upper)
  option(MORDICUS_MODULE_ENABLE_${name_upper} "Enable module ${name_upper}" ON)
  if (MORDICUS_MODULE_ENABLE_${name_upper})
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



#
# Module Cemosis
#
OPTION(MORDICUS_ENABLE_CEMOSIS "Enable Cemosis Module" OFF)
if ( MORDICUS_ENABLE_CEMOSIS)
  if ( ${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_CURRENT_SOURCE_DIR} )
    find_package(Feel++ COMPONENTS Toolboxes PATHS $ENV{FEELPP_DIR}/share/feelpp/feel/cmake/modules /usr/share/feelpp/feel/cmake/modules /usr/local/share/feelpp/feel/cmake/modules )
    if(NOT FEELPP_FOUND)
      message(FATAL_ERROR "[mordicus] Feel++ was not found on your system. Make sure to install it and specify the FEELPP_DIR to reference the installation directory.")
    endif()
    if (NOT FEELPP_TOOLBOXES_FOUND)
      message(FATAL_ERROR "[mordicus] Feel++ was not installed with toolboxes")
    endif()
    message("[mordicus] enabling cemosis module with an installation of feel++")
  else()
    message("[mordicus] enabling cemosis module with feel++")
    feelpp_get_environment()
    set(FEELPP_DIR ${CMAKE_INSTALL_PREFIX})
  endif()
  add_subdirectory(cemosis)
endif(MORDICUS_ENABLE_CEMOSIS)
