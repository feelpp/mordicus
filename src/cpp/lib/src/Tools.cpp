#include <algorithm>
#include <cctype>
#include "mordicus/core/Tools.hpp"

namespace mordicus
{
    std::string Tools::ToLower(const std::string& str)
    {
        std::string ret(str);
        std::transform(str.begin(), str.end(), ret.begin(), [](unsigned char c){ return std::tolower(c); });
        return ret;
    }

    std::string Tools::GetSharedLibraryExtension()
    {
#ifdef _WIN32
      return ".dll";
#else
  #ifdef __APPLE__
      return ".dylib";
  #else
      return ".so";
  #endif
#endif
    }
}
