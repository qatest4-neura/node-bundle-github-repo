#ifndef NODE_TEMPLATE_CPP_STRING_PUBLISHER_HPP
#define NODE_TEMPLATE_CPP_STRING_PUBLISHER_HPP

#include <std_msgs/msg/string.hpp>

#include <neuraverse_sdk/NodeBase.hpp>
#include <neuraverse_sdk/utils/Config.hpp>

namespace node_template_cpp
{

// StringPublisher publishes a configurable text string on its `text_output`
// port every time the node is triggered (onExecute). The output is a
// std_msgs/String, which matches the EchoNode's `text_input` port so the two can
// be wired together directly in the NodeGraph editor.
class StringPublisher : public neuraverse::sdk::NodeBase
{
public:
    StringPublisher() = default;
    ~StringPublisher() override = default;

    void onExecute() override
    {
        std_msgs::msg::String msg;
        msg.data = text_;

        logInfo("Publishing text_output=\"" + msg.data + "\"");
        publish<std_msgs::msg::String>("text_output", msg);
    }

    void onConfigure(const NodeConfigStringMap& config,
                     const NodeConfigEntryMap* dynamic_config = nullptr) override
    {
        auto text = neuraverse::sdk::utils::getConfigValue("text", config, dynamic_config);
        if (text.has_value())
        {
            text_ = *text;
        }

        logInfo("StringPublisher configured: text=\"" + text_ + "\"");
    }

    void onStop() override
    {
        logInfo("StringPublisher stopped");
    }

    NodeConfigEntryMap onGetConfiguration() override
    {
        namespace nv_business = neuraverse::models::v1::gen::business;
        NodeConfigEntryMap entries;

        nv_business::NodeConfigEntry text_entry;
        text_entry.mutable_configvalue()->set_stringvalue(text_);
        text_entry.set_displaylabel("Text");
        text_entry.set_description("The string to publish on text_output each tick.");
        text_entry.set_required(false);
        text_entry.set_isoverridable(true);
        entries["text"] = std::move(text_entry);

        return entries;
    }

private:
    std::string text_ = "Hello from StringPublisher";
};

} // namespace node_template_cpp

#endif // NODE_TEMPLATE_CPP_STRING_PUBLISHER_HPP
