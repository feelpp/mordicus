add_library(cemosis_core INTERFACE)
add_library(mordicus::cemosis_core ALIAS cemosis_core)
target_include_directories(cemosis_core INTERFACE 
      $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/cpp/lib>
      $<INSTALL_INTERFACE:include/cemosis/> )
target_link_libraries(cemosis_core INTERFACE Feelpp::feelpp_contrib)
INSTALL(TARGETS cemosis_core DESTINATION lib/ COMPONENT Libs EXPORT cemosis_core-export-targets)
install(EXPORT cemosis_core-export-targets NAMESPACE mordicus:: DESTINATION share/mordicus/modules)
