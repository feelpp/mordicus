cmake_minimum_required (VERSION 3.2)

if (NOT DEFINED CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
endif ()

project (Mordicus)

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

set (CMAKE_CXX_STANDARD 17)

enable_testing()
add_subdirectory (lib)

if (BUILD_PYTHON)
  find_package (PythonInterp)
  find_package (PythonLibs ${PYTHON_VERSION_STRING} EXACT)
  set (PYTHON_INCLUDE_DIRS_BAK "${PYTHON_INCLUDE_DIRS}")

  set (PYBIND11_NOPYTHON ON)
  find_package (pybind11 2.2 CONFIG)

  if (pybind11_FOUND)
    if (pybind11_VERSION VERSION_LESS 2.6)
      message(STATUS "Found pybind11: ${pybind11_INCLUDE_DIR} (found version ${pybind11_VERSION})")
    endif ()
    list(APPEND CMAKE_MODULE_PATH ${pybind11_DIR})
    include (pybind11Tools)
  endif ()
  if (PythonLibs_FOUND AND pybind11_FOUND)
    add_subdirectory (python)
  endif ()
endif ()



