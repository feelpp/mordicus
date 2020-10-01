#pragma once
#include "mordicus/core/ModuleBase.hpp"
#include "mordicus/core/container/mesh/MeshBase.hpp"

namespace mordicus {

template <typename Elem, typename Node>
class MeshReaderBase : public ModuleBase {
public:
    MeshReaderBase() {}
    MeshReaderBase(const std::string& /*_filename*/) {}
    ~MeshReaderBase() {}

    std::string getType() { return "MeshReader"; }
    virtual MeshBase<Elem, Node>* readMesh() = 0;
};
}
