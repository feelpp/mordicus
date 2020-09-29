#pragma once

#include <vector>
#include "MeshStorageBase.hxx"
#include "SciMordicus.hxx"

class SciStorage : public mordicus::MeshStorageBase {
public:
    SciStorage() {}
    ~SciStorage() {}

    std::string getName() { return "SciStorage"; }

    void addNode(const SCINODE& node) { nodes.push_back(node); }
    void addElement(const SCIELEM& element) { elements.push_back(element); }

    std::vector<SCINODE>  nodes;
    std::vector<SCIELEM>  elements;
};
