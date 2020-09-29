#pragma once

#include "dynlib_scimesh.h"
#include "MeshBase.hxx"
#include "SciStorage.hxx"

class SciMesh;

#if __cplusplus
extern "C" {
#endif
    SCIMESH_IMPEXP mordicus::ModuleBase* getInstance(SciStorage* storage);
    SCIMESH_IMPEXP void deleteInstance(SciMesh* inst);
#if __cplusplus
}
#endif
