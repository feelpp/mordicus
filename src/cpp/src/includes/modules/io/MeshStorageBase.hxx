#pragma once
#include "ModuleBase.hxx"

namespace mordicus {
class MeshStorageBase : public ModuleBase {
public:
    MeshStorageBase() {}
    ~MeshStorageBase() {}

    std::string getType() { return "MeshStorage"; }
};
}