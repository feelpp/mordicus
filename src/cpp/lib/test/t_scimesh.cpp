#include <iostream>
#include <string>

//modicus kernel
#include "mordicus/core/Mordicus.hpp"

//my adapted module
#include "SciMeshReader.hpp"
#include "SciMesh.hpp"

int main() {
    mordicus::Mordicus* m = mordicus::Mordicus::getMordicusInstance();
    try
    {
        m->initialize("t_scimesh.json");
    }
    catch (std::exception& e)
    {
        std::cout << "exception: " << e.what() << std::endl;
        return 1;
    }

    SciMeshReader* reader = m->getModuleInstance("io", "SciMeshReader", (std::string)"my file")->As<SciMeshReader>();
    std::cout << "Name: " << reader->getName() << std::endl;

    SciMesh* mesh = reader->readMesh()->As<SciMesh>();
    std::cout << "Nodes: " << mesh->getNumbersOfNodes() << std::endl;

    m->deleteModuleInstance("io", "SciMeshReader", reader);
    return 0;
}
