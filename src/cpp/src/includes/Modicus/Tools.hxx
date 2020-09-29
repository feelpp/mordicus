#pragma once
#include <string>
#include <algorithm>
#include <cctype>

#include "dynlib_mordicus.h"

namespace mordicus
{
class MORDICUS_API Tools
{
public:
    static std::string toLower(const std::string& str);
};
}
