#pragma once

#include <tuple>
#include <mordicus/core/container/mesh/MeshBase.hpp>
#include <mordicus/module/cemosis/core/mordicus.hpp>
#include <mordicus/module/cemosis/core/storage.hpp>

namespace mordicus::module::cemosis
{
class Mesh : public mordicus::MeshBase <Elem, Node>
{
public:
    Mesh(Storage* _storage) : storage(_storage) {}
    virtual ~SciMesh() {}

    std::string getName() { return "Mesh"; }
#if 0
    NODES getNodes();
    virtual ELEM_ITERATOR elementsIterator();
    virtual int64_t getNumbersOfNodes();
    virtual int64_t getDimensionality();
    virtual ELEM_LIST getElemAttach(int rank);
    virtual int getElemContaining(int rank);
#endif
private:
    Storage* getStorage();
    Storage* storage;
};
}
