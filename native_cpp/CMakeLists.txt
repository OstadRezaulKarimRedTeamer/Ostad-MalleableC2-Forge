cmake_minimum_required(VERSION 3.15)
project(OstadMalleableC2 VERSION 4.2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

# Platform socket libraries
if(WIN32)
    set(NET_LIBS ws2_32)
else()
    set(NET_LIBS "")
endif()

# 1. Main Workbench & Linter Tool
add_executable(OstadMalleableC2
    src/main.cpp
    include/MalleableModels.hpp
    include/MalleableTransforms.hpp
    include/MalleableSerializer.hpp
    include/MalleableParser.hpp
    include/MalleableGenerator.hpp
    include/MalleableLinter.hpp
    include/MalleableTrafficSim.hpp
    include/MalleableDetection.hpp
)

# 2. Separate C2 Server Daemon
add_executable(OstadC2_Server
    server/main_server.cpp
    server/Server.hpp
    include/MalleableModels.hpp
    include/MalleableTransforms.hpp
    include/MalleableParser.hpp
    include/MalleableSerializer.hpp
    include/MalleableGenerator.hpp
)
target_link_libraries(OstadC2_Server PRIVATE ${NET_LIBS})

# 3. Separate C2 Client Agent
add_executable(OstadC2_Client
    client/main_client.cpp
    client/Client.hpp
    include/MalleableModels.hpp
    include/MalleableTransforms.hpp
    include/MalleableParser.hpp
    include/MalleableGenerator.hpp
)
target_link_libraries(OstadC2_Client PRIVATE ${NET_LIBS})

# Optimization flags for release builds
if(MSVC)
    target_compile_options(OstadMalleableC2 PRIVATE /W4 /O2 /permissive-)
    target_compile_options(OstadC2_Server PRIVATE /W4 /O2 /permissive-)
    target_compile_options(OstadC2_Client PRIVATE /W4 /O2 /permissive-)
else()
    target_compile_options(OstadMalleableC2 PRIVATE -Wall -Wextra -O3)
    target_compile_options(OstadC2_Server PRIVATE -Wall -Wextra -O3)
    target_compile_options(OstadC2_Client PRIVATE -Wall -Wextra -O3)
endif()
