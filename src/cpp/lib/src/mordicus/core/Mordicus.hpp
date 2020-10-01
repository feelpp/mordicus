#pragma once

#include <iostream>
#include <unordered_map>
#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif
#include "mordicus/mordicus_export.h"
#include "mordicus/core/ModuleBase.hpp"
#include "mordicus/core/Tools.hpp"

namespace mordicus {
typedef std::unordered_map<std::string, std::string> Module;
typedef std::unordered_map<std::string, Module> Modules;

class MORDICUS_EXPORT Mordicus {
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
            throw std::runtime_error("Module does not exist");
        }

        std::string library = c->second;
#ifdef _WIN32
        HMODULE hmod = LoadLibraryA(library.c_str());
        if (hmod == NULL)
        {
            throw std::runtime_error("Library not found");
        }

        typedef ModuleBase* (*MODULE_INSTANCE)(Args...);
        MODULE_INSTANCE getInstance = (MODULE_INSTANCE)GetProcAddress(hmod, "getInstance");
        if (getInstance == nullptr)
        {
            throw std::runtime_error("getInstance not found");
        }
#else
        void *hmod = dlopen(library.c_str(), RTLD_NOW);
        if (!hmod)
        {
          dlerror();
          throw std::runtime_error("Library not found");
        }
        typedef ModuleBase* (*pf)(Args... args);
        pf getInstance = (pf) dlsym(hmod, "getInstance");	
#endif
        ModuleBase* result = getInstance(args...);
#ifndef _WIN32
        dlclose(hmod); 
#endif
        return result;
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
            throw std::runtime_error("Module does not exist");
        }

        std::string library = c->second;
#ifdef _WIN32
        HMODULE hmod = LoadLibraryA(library.c_str());
        if (hmod == NULL)
        {
            throw std::runtime_error("Library not found");
        }
        typedef ModuleBase* (*DELETE_INSTANCE)(T*);
        DELETE_INSTANCE deleteInstance = (DELETE_INSTANCE)GetProcAddress(hmod, "deleteInstance");
        if (deleteInstance == nullptr)
        {
            throw std::runtime_error("deleteInstance not found");
        }
#else
        void *hmod = dlopen(library.c_str(), RTLD_NOW);
        if (!hmod)
        {
          dlerror();
          throw std::runtime_error("Library not found");
        }
        typedef ModuleBase* (*pf)(T*);
        pf deleteInstance = (pf) dlsym(hmod, "deleteInstance");	

#endif
        ModuleBase* result = deleteInstance(inst);
#ifndef _WIN32
        dlclose(hmod); 
#endif
        return result;
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
