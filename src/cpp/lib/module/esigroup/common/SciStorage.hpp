#pragma once

#include <vector>
#include <mordicus/core/io/MeshStorageBase.hpp>
#include "SciMordicus.hpp"

class SciStorage : public mordicus::MeshStorageBase {
public:
    SciStorage() {}
    virtual ~SciStorage() {}

    std::string getName() { return "SciStorage"; }

    void addNode(const SCINODE& node) { nodes.push_back(node); }
    void addElement(const SCIELEM& element) { elements.push_back(element); }

    std::vector<SCINODE>  nodes;
    std::vector<SCIELEM>  elements;
};
