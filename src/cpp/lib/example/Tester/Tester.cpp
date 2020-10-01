#include <iostream>
#include <string>

//modicus kernel
#include "Mordicus.hxx"

//my adapted module
#include "SciMeshReader.hxx"
#include "SciMesh.hxx"

int main() {
    mordicus::Mordicus* m = mordicus::Mordicus::getMordicusInstance();
    try
    {
        m->initialize("../exemples/Tester/config/mordicus.json");
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
