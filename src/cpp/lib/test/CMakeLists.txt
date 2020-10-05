
macro(mordicus_add_test name)
  add_executable (t_${name} t_${name}.cpp)
  target_link_libraries (t_${name} PUBLIC mordicus)
  add_test(NAME ${name} COMMAND t_${name})
  set_tests_properties(${name} PROPERTIES ENVIRONMENT "LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/lib/module")
endmacro()

mordicus_add_test (scimesh)
target_link_libraries (t_scimesh PUBLIC SciMeshReader)
file (COPY ${CMAKE_CURRENT_SOURCE_DIR}/t_scimesh.json DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
