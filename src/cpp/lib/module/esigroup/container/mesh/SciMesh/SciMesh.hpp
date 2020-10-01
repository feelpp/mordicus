#pragma once

#include <tuple>
#include <mordicus/core/container/mesh/MeshBase.hpp>
#include "SciMordicus.hpp"
#include "SciStorage.hpp"

class SciMesh : public mordicus::MeshBase <SCIELEM, SCINODE>
{
public:
    SciMesh(SciStorage* _storage) : storage(_storage) {}
    virtual ~SciMesh() {}

    std::string getName() { return "SciMesh"; }

    NODES getNodes();
    virtual ELEM_ITERATOR elementsIterator();
    virtual int64_t getNumbersOfNodes();
    virtual int64_t getDimensionality();
    virtual ELEM_LIST getElemAttach(int rank);
    virtual int getElemContaining(int rank);

private:
    SciStorage* getStorage();
    SciStorage* storage;
};
