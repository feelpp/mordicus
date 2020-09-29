#pragma once

#include <iostream>
#include <unordered_map>
#include <Windows.h>

#include "dynlib_mordicus.h"
#include "ModuleBase.hxx"
#include "Tools.hxx"

namespace mordicus {
typedef std::unordered_map<std::string, std::string> Module;
typedef std::unordered_map<std::string, Module> Modules;

class MORDICUS_API Mordicus {
public:
    static Mordicus* getMordicusInstance();
    static void deleteMordicusInstance();

    void registerModule(const std::string& type, const std::string& lang, const std::string& name, const std::string& library);

    template <class ...Args>
    ModuleBase* operator()(const std::string& type, const std::string& module, Args... args) {
        return getModuleInstance(type, module, args...);
    }

    template <class ...Args>
    ModuleBase* getModuleInstance(const std::string& type, const std::string& module, Args... args)
    {
        std::string _type = Tools::toLower(type);
        std::string _module = Tools::toLower(module);

        Module& m = getModule(_type);
        auto c = m.find(_module);
        if (c == m.end())
        {
            throw std::exception("Module does not exist");
        }

        std::string library = c->second;
        HMODULE hmod = LoadLibraryA(library.c_str());
        if (hmod == NULL)
        {
            throw std::exception("Library not found");
        }

        typedef ModuleBase* (*MODULE_INSTANCE)(Args...);
        MODULE_INSTANCE getInstance = (MODULE_INSTANCE)GetProcAddress(hmod, "getInstance");
        if (getInstance == nullptr)
        {
            throw std::exception("getInstance not found");
        }

        return getInstance(args...);
    }

    template <class T>
    ModuleBase* deleteModuleInstance(const std::string& type, const std::string& module, T* inst)
    {
        std::cout << "type: " << inst->getType() << std::endl;
        std::cout << "name: " << inst->getName() << std::endl;
        std::string _type = Tools::toLower(type);
        std::string _module = Tools::toLower(module);

        Module& m = getModule(_type);
        auto c = m.find(_module);
        if (c == m.end())
        {
            throw std::exception("Module does not exist");
        }

        std::string library = c->second;
        HMODULE hmod = LoadLibraryA(library.c_str());
        if (hmod == NULL)
        {
            throw std::exception("Library not found");
        }

        typedef ModuleBase* (*DELETE_INSTANCE)(T*);
        DELETE_INSTANCE deleteInstance = (DELETE_INSTANCE)GetProcAddress(hmod, "deleteInstance");
        if (deleteInstance == nullptr)
        {
            throw std::exception("deleteInstance not found");
        }

        return deleteInstance(inst);
    }

    bool initialize(const std::string& file);
    bool isInitialize() { return init; }

private:
    Mordicus() : init(false) {/*init logger system, probably load config and pathbuilding, ...*/ }
    virtual ~Mordicus() {}

    Module& getModule(const std::string& type);

    Modules modules;

private:
    bool init;
    static Mordicus* instance;
};
}
