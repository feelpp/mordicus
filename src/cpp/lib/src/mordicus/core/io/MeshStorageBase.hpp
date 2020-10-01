#pragma once
#include "mordicus/core/ModuleBase.hpp"

namespace mordicus {
class MeshStorageBase : public ModuleBase {
public:
    MeshStorageBase() {}
    ~MeshStorageBase() {}

    std::string getType() { return "MeshStorage"; }
};
}
