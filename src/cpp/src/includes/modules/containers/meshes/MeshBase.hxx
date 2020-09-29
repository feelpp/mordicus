#pragma once
#include <vector>
#include <list>
#include "ModuleBase.hxx"
#include "MeshStorageBase.hxx"

namespace mordicus {

template <typename Elem, typename Node>
class MeshBase : public ModuleBase
{
public:
    typedef std::vector<Node> NODES;
    typedef std::vector<Elem> ELEM;
    typedef typename ELEM::iterator ELEM_ITERATOR;
    typedef std::list<Elem> ELEM_LIST;

    MeshBase() {}
    ~MeshBase() {}

    /*virtual*/
    virtual void setStorage(MeshStorageBase* _storage) { storage = _storage; }
    virtual MeshStorageBase* getStorage() { return storage; }

    /*pure vitual*/
    virtual NODES getNodes() = 0;
    virtual ELEM_ITERATOR elementsIterator() = 0;
    virtual int64_t getNumbersOfNodes() = 0;
    virtual int64_t getDimensionality() = 0;
    virtual ELEM_LIST getElemAttach(int rank) = 0;
    virtual int getElemContaining(int ip_rk) = 0;

    std::string getType() { return "MeshBase"; }

private: 
    MeshStorageBase* storage;
};
}