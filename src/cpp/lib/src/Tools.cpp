#include <algorithm>
#include <cctype>
#include "mordicus/core/Tools.hpp"

namespace mordicus
{
    std::string Tools::toLower(const std::string& str)
    {
        std::string ret(str);
        std::transform(str.begin(), str.end(), ret.begin(), [](unsigned char c){ return std::tolower(c); });
        return ret;
    }
}
