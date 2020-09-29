#pragma once

#ifdef SCIMESHREADER_EXPORTS
#define SCIMESHREADER_IMPEXP __declspec(dllexport)
#else
#define SCIMESHREADER_IMPEXP __declspec(dllimport)
#endif
