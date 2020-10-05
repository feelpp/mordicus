
pybind11_add_module(mordicus_python main.cpp)
target_link_libraries(mordicus_python PRIVATE mordicus pybind11::module)
set_target_properties(mordicus_python PROPERTIES OUTPUT_NAME mordicus)

if (WIN32)
  set (PYTHON_SITE_PACKAGES Lib/site-packages)
else ()
  set (PYTHON_SITE_PACKAGES ${CMAKE_INSTALL_LIBDIR}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages)
endif ()

install(TARGETS mordicus_python DESTINATION ${PYTHON_SITE_PACKAGES})
