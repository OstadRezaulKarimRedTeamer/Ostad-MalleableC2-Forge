CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -O3 -Iinclude
NET_LIBS ?= -lws2_32

TARGETS = OstadMalleableC2 OstadC2_Server OstadC2_Client

all: $(TARGETS)

OstadMalleableC2: src/main.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

OstadC2_Server: server/main_server.cpp server/Server.hpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(NET_LIBS)

OstadC2_Client: client/main_client.cpp client/Client.hpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(NET_LIBS)

clean:
	rm -f $(TARGETS) *.exe
