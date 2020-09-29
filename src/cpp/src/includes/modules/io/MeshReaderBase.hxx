#pragma once
#include "ModuleBase.hxx"
#include "MeshBase.hxx"

namespace mordicus {

template <typename Elem, typename Node>
class MeshReaderBase : public ModuleBase {
public:
    MeshReaderBase() {}
    MeshReaderBase(const std::string& _filename) {}
    ~MeshReaderBase() {}

    std::string getType() { return "MeshReader"; }
    virtual MeshBase<Elem, Node>* readMesh() = 0;
};
}