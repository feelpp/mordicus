#pragma once
#include <string>

namespace mordicus {
class  ModuleBase {
public:
    ModuleBase() {}
    ~ModuleBase() {}

    template <class T>
    T* As() { return static_cast<T*>(this); }

    virtual std::string getType() = 0;
    virtual std::string getName() = 0;
};
}