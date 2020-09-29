#pragma once
#include "dynlib_scimeshreader.h"
#include <MeshReaderBase.hxx>
#include <MeshBase.hxx>

#include "SciStorage.hxx"
#include "SciMordicus.hxx"
#include "SciMesh.hxx"

class SciMeshReader : public mordicus::MeshReaderBase<SCIELEM, SCINODE>
{
public:
    SciMeshReader() : storage(nullptr) {}
    SciMeshReader(const std::string& _filename);
    virtual ~SciMeshReader();

    std::string getName() { return "SciMeshReader"; }
    
    virtual mordicus::MeshBase<SCIELEM, SCINODE>* readMesh();

    SciMesh* getMesh() { return mesh; }

private:
    std::string filename;
    SciStorage* storage;
    SciMesh* mesh;
};

extern "C" {
    SCIMESHREADER_IMPEXP mordicus::ModuleBase* getInstance(const std::string& filename);
    SCIMESHREADER_IMPEXP void deleteInstance(SciMeshReader* reader);
}
