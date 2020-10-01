#pragma once
#include <mordicus/core/io/MeshReaderBase.hpp>
#include <mordicus/core/container/mesh/MeshBase.hpp>

#include "scimeshreader_export.h"
#include "SciStorage.hpp"
#include "SciMordicus.hpp"
#include "SciMesh.hpp"

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
    SCIMESHREADER_EXPORT mordicus::ModuleBase* getInstance(const std::string& filename);
    SCIMESHREADER_EXPORT void deleteInstance(SciMeshReader* reader);
}
