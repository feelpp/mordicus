#include <iostream>
#include <fstream>

#include "mordicus/core/Mordicus.hpp"

#include "nlohmann/json.hpp"
using json = nlohmann::json;

namespace mordicus {
Mordicus* Mordicus::instance = nullptr;

Mordicus* Mordicus::getMordicusInstance()
{
    if (instance == nullptr)
    {
        instance = new Mordicus();
    }

    return instance;
}

void Mordicus::deleteMordicusInstance()
{
    if (instance)
    {
        delete instance;
    }

    instance = nullptr;
}

void Mordicus::registerModule(const std::string& type, const std::string& /*lang*/, const std::string& module, const std::string& library)
{
    std::string _type = Tools::toLower(type);
    std::string _module = Tools::toLower(module);
    if (modules.find(_type) == modules.end())
    {
        modules[_type][_module] = "";
    }

    if (modules[_type][_module] != "")
    {
        throw std::runtime_error("Already exists !");
    }

    try
    {
        modules[_type][_module] = library;
    }
    catch (std::exception& e)
    {
        //logger
        throw e;
    }
}

bool Mordicus::initialize(const std::string & configFile)
{
    ///check file, blabla, ..
    std::ifstream config(configFile);
    json j;
    config >> j;
    if (j.contains("modules"))
    {
        json m = j["modules"];

        //check all categories

        if (m.contains("io"))
        {
            json adaptee = m["io"][0];
            registerModule("io", adaptee["type"], adaptee["name"], adaptee["library"]);
        }

        if (m.contains("containers"))
        {
            if (m["containers"].contains("mesh"))
            {
                json adaptee = m["containers"]["mesh"][0];
                registerModule("mesh", "native", adaptee["name"], adaptee["library"]);
            }
        }
    }

    init = true;
    return true;
}

Module& Mordicus::getModule(const std::string& type)
{
    auto p = modules.find(type);
    if (p != modules.end()) {
        return p->second;
    }
    else
    {
        throw std::runtime_error("pas bien");
    }
}
}
