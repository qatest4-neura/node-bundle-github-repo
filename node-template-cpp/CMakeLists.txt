cmake_minimum_required(VERSION 3.16)
project(node_template_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(neuraverse_node_sdk REQUIRED CONFIG)

add_executable(node_template_cpp
    src/main.cpp
)
target_include_directories(node_template_cpp PRIVATE src)
target_link_libraries(node_template_cpp PRIVATE neuraverse_node_sdk)
