#pragma once

#ifdef SCIMESH_EXPORTS
#define SCIMESH_IMPEXP __declspec(dllexport)
#else
#define SCIMESH_IMPEXP __declspec(dllimport)
#endif
