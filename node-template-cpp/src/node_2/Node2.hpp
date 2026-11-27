#ifndef NODE_TEMPLATE_CPP_NODE2_HPP
#define NODE_TEMPLATE_CPP_NODE2_HPP

#include <neuraverse_sdk/NodeBase.hpp>

namespace node_template_cpp
{

/// A minimal example node that does nothing — use as a starting point.
class Node2 : public neuraverse::sdk::NodeBase
{
public:
    Node2() = default;
    ~Node2() override = default;

    void onExecute() override
    {
        logInfo("Executing Node2 ...");
    }

    void onConfigure(const NodeConfigStringMap& /*config*/,
                     const NodeConfigEntryMap* /*dynamic_config*/) override
    {
    }

    void onStop() override
    {
        logInfo("Node2 stopped");
    }

    NodeConfigEntryMap onGetConfiguration() override
    {
        NodeConfigEntryMap entries;
        return entries;
    }
};

} // namespace node_template_cpp

#endif // NODE_TEMPLATE_CPP_NODE2_HPP
