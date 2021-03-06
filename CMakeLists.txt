cmake_minimum_required (VERSION 3.2)

if (NOT DEFINED CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
endif ()

project (mordicus VERSION 0.1.0)

option (BUILD_SHARED_LIBS "build shared/static libs" ON)
option (BUILD_PYTHON "build Python module" ON)

include (GenerateExportHeader)
include (CMakePackageConfigHelpers)
include (GNUInstallDirs)

configure_package_config_file ( 
  "${PROJECT_SOURCE_DIR}/mordicus-config.cmake.in" 
  "${PROJECT_BINARY_DIR}/mordicus-config.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mordicus)
install (FILES "${PROJECT_BINARY_DIR}/mordicus-config.cmake" DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mordicus)

if (NOT DEFINED MORDICUS_STD_CPP )
  set(MORDICUS_STD_CPP "17") # values can be : 17, 20
endif()
set (CMAKE_CXX_STANDARD ${MORDICUS_STD_CPP})

enable_testing()
add_subdirectory (src/cpp/lib)

if (BUILD_PYTHON)
  find_package (PythonInterp)
  find_package (PythonLibs ${PYTHON_VERSION_STRING} EXACT)
  set (PYTHON_INCLUDE_DIRS_BAK "${PYTHON_INCLUDE_DIRS}")

  set (PYBIND11_NOPYTHON ON)
  find_package (pybind11)# 2.2 CONFIG)

  if (pybind11_FOUND)
    if (pybind11_VERSION VERSION_LESS 2.6)
      message(STATUS "Found pybind11: ${pybind11_INCLUDE_DIR} (found version ${pybind11_VERSION})")
    endif ()
    list(APPEND CMAKE_MODULE_PATH ${pybind11_DIR})
    include (pybind11Tools)
  endif ()
  if (PythonLibs_FOUND AND pybind11_FOUND)
    add_subdirectory (src/cpp/python)
  endif ()
endif ()

add_subdirectory(src/poc-1)


set(CPACK_PACKAGE_NAME "${PROJECT_NAME}-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${EXTRA_VERSION}")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}${EXTRA_VERSION}")
SET(CPACK_PACKAGE_FILE_NAME "${PROJECT_NAME}-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${EXTRA_VERSION}-${CMAKE_SYSTEM_NAME}")
set(CPACK_PACKAGE_DIRECTORY "${PROJECT_BINARY_DIR}/assets")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Mordicus Framework")
set(CPACK_PACKAGE_DESCRIPTION "Mordicus framework.")
set(CPACK_PACKAGE_VENDOR "Mordicus")
set(CPACK_PACKAGE_CONTACT "<contact mordicus>")
set(CPACK_PACKAGE_VERSION_MAJOR "${PROJECT_VERSION_MAJOR}")
set(CPACK_PACKAGE_VERSION_MINOR "${PROJECT_VERSION_MINOR}")
set(CPACK_PACKAGE_VERSION_PATCH "${PROJECT_VERSION_PATCH}")


set(CPACK_GENERATOR "TGZ;DEB")
set(CPACK_SOURCE_GENERATOR "TGZ")


set(CPACK_DEBIAN_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "libfeelpp-toolboxes1-fluid (>= 0.110), feelpp-tools (>= 0.110), python3-feelpp-toolboxes-fluid (>= 0.110)")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "${CPACK_PACKAGE_DESCRIPTION_SUMMARY}")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION "${CPACK_PACKAGE_DESCRIPTION}")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")
set(CPACK_DEBIAN_PACKAGE_SECTION "science")
set(CPACK_DEBIAN_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}${EXTRA_VERSION}")
set(CPACK_DEBIAN_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")
#set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "${CMAKE_SOURCE_DIR}/cmake/debian/postinst")

include(CPack)
