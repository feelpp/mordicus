#pragma once

#include <mordicus/core/container/mesh/MeshBase.hpp>
#include "SciStorage.hpp"
#include "scimesh_export.h"

class SciMesh;

#if __cplusplus
extern "C" {
#endif
    SCIMESH_EXPORT mordicus::ModuleBase* getInstance(SciStorage* storage);
    SCIMESH_EXPORT void deleteInstance(SciMesh* inst);
#if __cplusplus
}
#endif
