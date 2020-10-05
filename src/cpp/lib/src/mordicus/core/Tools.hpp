#pragma once
#include <string>
#include <algorithm>
#include <cctype>

#include "mordicus/mordicus_export.h"

namespace mordicus
{
class MORDICUS_EXPORT Tools
{
public:
    static std::string ToLower(const std::string& str);

    static std::string GetSharedLibraryExtension();

};
}
