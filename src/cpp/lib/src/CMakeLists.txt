
add_library (mordicus Mordicus.cpp Tools.cpp)
generate_export_header (mordicus)
file (COPY ${CMAKE_CURRENT_BINARY_DIR}/mordicus_export.h DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/mordicus)

target_include_directories (mordicus PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_include_directories (mordicus PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

install(TARGETS mordicus
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY mordicus DESTINATION include)

