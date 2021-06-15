#pragma once

#include <mordicus/module/cemosis/core/mordicus.hpp>
#include <mordicus/core/io/MeshStorageBase.hpp>
#include <vector>

namespace mordicus::module::cemosis
{
class Storage : public mordicus::MeshStorageBase
{
  public:
    Storage() = default;
    virtual ~Storage() = default;

    std::string getName() { return "CemosisStorage"; }

    void addNode( const Node& node ) { nodes.push_back( node ); }
    void addElement( const Elem& element ) { elements.push_back( element ); }

    std::vector<Node> nodes;
    std::vector<Elem> elements;
};
} // namespace mordicus::module::cemosis

