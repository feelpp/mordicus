cmake_minimum_required (VERSION 3.2)

if (NOT DEFINED CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
endif ()

project (Mordicus)

option (BUILD_SHARED_LIBS "build shared/static libs" ON)
option (BUILD_PYTHON "build Python module" OFF)

include (GenerateExportHeader)
include (GNUInstallDirs)

set (CMAKE_CXX_STANDARD 17)

enable_testing()
add_subdirectory (lib)

if (BUILD_PYTHON)
  find_package (PythonInterp)
  find_package (PythonLibs)
  if (PythonLibs_FOUND)
    add_subdirectory (python)
  endif ()
endif ()

