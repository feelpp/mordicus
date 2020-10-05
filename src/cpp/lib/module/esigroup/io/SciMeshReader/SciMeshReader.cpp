#include <cmath>

#include <mordicus/core/Mordicus.hpp>
#include "SciMeshReader.hpp"

const double pi = std::acos(-1);

mordicus::ModuleBase* getInstance(const std::string& filename)
{
    return new SciMeshReader(filename);
}

void deleteInstance(SciMeshReader * reader)
{
    mordicus::Mordicus* m = mordicus::Mordicus::getMordicusInstance();
    m->deleteModuleInstance("mesh", "SciMesh", reader->getMesh());
    delete reader;
}

SciMeshReader::~SciMeshReader()
{
    if (storage)
    {
        delete storage;
    }
}

SciMeshReader::SciMeshReader(const std::string & _filename) : filename(_filename), storage(nullptr)
{
    //create a fake mesh (triforce)
    //     4
    //     /\         //
    //  2 /__\ 5
    //   /\  /\       //
    //  /__\/__\      //
    // 1   3    6

    storage = new SciStorage();
    storage->addNode(SCINODE(0, 0));
    storage->addNode(SCINODE(2, 2 / std::tan(pi / 6)));
    storage->addNode(SCINODE(4, 0));
    storage->addNode(SCINODE(4, 4 / std::tan(pi / 6)));
    storage->addNode(SCINODE(6, 0));
    storage->addNode(SCINODE(8, 2 / std::tan(pi / 6)));

    //left
    storage->addElement(SCIELEM(1, 2, 3));
    //top
    storage->addElement(SCIELEM(2, 4, 5));
    //right
    storage->addElement(SCIELEM(3, 5, 6));
}

mordicus::MeshBase<SCIELEM, SCINODE>* SciMeshReader::readMesh()
{
    mordicus::Mordicus* m = mordicus::Mordicus::getMordicusInstance();
    mesh = (*m)("mesh", "SciMesh", storage)->As<SciMesh>();
    return mesh;
}
