
macro(mordicus_add_test name)
  add_test(NAME pycheck_${name} COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/t_${name}.py)
  set_tests_properties(pycheck_${name} PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}/../src")
endmacro()

mordicus_add_test (Mordicus)

