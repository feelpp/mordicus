
add_library (mordicus Mordicus.cpp Tools.cpp)
target_compile_features(mordicus PUBLIC cxx_std_${MORDICUS_STD_CPP})
generate_export_header (mordicus)
file (COPY ${CMAKE_CURRENT_BINARY_DIR}/mordicus_export.h DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/mordicus)

find_library (LIBDL_LIBRARY NAMES dl)
if (LIBDL_LIBRARY)
  target_link_libraries(mordicus PUBLIC ${LIBDL_LIBRARY})
endif ()

target_include_directories(mordicus PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR};${CMAKE_CURRENT_BINARY_DIR}>"
  $<INSTALL_INTERFACE:include>
)

install(TARGETS mordicus
  EXPORT mordicus-targets
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

install(EXPORT mordicus-targets
        FILE mordicus-targets.cmake
        NAMESPACE mordicus::
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mordicus)

install(DIRECTORY mordicus DESTINATION include)

       
