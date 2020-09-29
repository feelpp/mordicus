#pragma once

#if MORDICUS_EXPORTS
#define MORDICUS_API __declspec(dllexport)
#else
#define MORDICUS_API __declspec(dllimport)
#endif
