#include <pybind11/pybind11.h>

#include "mordicus/core/Mordicus.hpp"


PYBIND11_MODULE(mordicus, m) {
  pybind11::class_<mordicus::Mordicus, std::unique_ptr<mordicus::Mordicus, pybind11::nodelete> >(m, "Mordicus")
        .def("isInitialize", &mordicus::Mordicus::isInitialize)
        .def("getMordicusInstance", &mordicus::Mordicus::getMordicusInstance);
}
