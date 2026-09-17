#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <neuraverse_sdk/NodeManagerService.hpp>

#include "string_publisher/StringPublisher.hpp"
#include "node_2/Node2.hpp"

static std::string env(const char* name, const std::string& fallback)
{
    const char* val = std::getenv(name);
    return (val != nullptr) ? std::string(val) : fallback;
}

int main()
{
    std::cout << "Starting node-template-cpp nodes..." << std::endl;

    neuraverse::sdk::NodeServiceConfig config;
    config.grpc.address = "0.0.0.0";
    config.grpc.port = std::stoi(env("NODE_GRPC_PORT", "50081"));
    config.http.address = "0.0.0.0";
    config.http.port = std::stoi(env("NODE_HTTP_PORT", "8081"));
    config.mqtt.broker_host = env("MQTT_BROKER_HOST", "localhost");
    config.mqtt.broker_port = std::stoi(env("MQTT_BROKER_PORT", "1883"));
    config.registry_config.registry_endpoint = env("CONSUL_ENDPOINT", "localhost:8500");

    std::string advertise_host = env("NODE_ADVERTISE_HOST", "");
    if (!advertise_host.empty())
    {
        config.registry_config.node_cluster_target =
            advertise_host + ":" + std::to_string(config.grpc.port);
    }

    std::vector<std::pair<std::string, neuraverse::sdk::NodeFactory>> node_classes = {
        {"StringPublisher", []() -> std::unique_ptr<neuraverse::sdk::NodeBase> {
            return std::make_unique<node_template_cpp::StringPublisher>();
        }},
        {"Node2", []() -> std::unique_ptr<neuraverse::sdk::NodeBase> {
            return std::make_unique<node_template_cpp::Node2>();
        }},
    };

    std::cout << "Registering " << node_classes.size() << " node(s):" << std::endl;
    for (const auto& [name, _] : node_classes)
    {
        std::cout << "  + " << name << std::endl;
    }

    neuraverse::sdk::NodeManagerService::run(node_classes, config);
    return 0;
}
