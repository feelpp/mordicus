#include <algorithm>
#include <cctype>
#include "Tools.hxx"

namespace mordicus
{
    std::string Tools::toLower(const std::string& str)
    {
        std::string ret(str);
        std::transform(str.begin(), str.end(), ret.begin(), std::tolower);
        return ret;
    }
}