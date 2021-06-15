#include <mordicus/module/cemosis/container/mesh/mesh.hpp>
#include <mordicus/module/cemosis/container/mesh/mesh.h>
#if 0
#include "SciMesh.hpp"
#include "SciMesh.h"

mordicus::ModuleBase* getInstance(SciStorage* storage) {
    return new SciMesh(storage);
}

void deleteInstance(SciMesh* inst) {
    delete inst;
}

SciStorage* SciMesh::getStorage()
{
    return storage;
}

SciMesh::NODES SciMesh::getNodes()
{
    return getStorage()->nodes;
}

SciMesh::ELEM_ITERATOR SciMesh::elementsIterator()
{
    return getStorage()->elements.begin();
}

int64_t SciMesh::getNumbersOfNodes()
{
   return getStorage()->nodes.size();
}

int64_t SciMesh::getDimensionality()
{
    // SBAM !
    return std::tuple_size<ELEM::value_type>::value;
}

SciMesh::ELEM_LIST SciMesh::getElemAttach(int rank)
{
    //aucune id�e de ce que cela repr�sente ...
    if (rank >= (int)getStorage()->elements.size())
    {
        return {};
    }

    return { getStorage()->elements[rank] };
}

int SciMesh::getElemContaining(int /*rank*/)
{
    //aucune id�e de ce que cela repr�sente ...
    return 0;
}
#endif