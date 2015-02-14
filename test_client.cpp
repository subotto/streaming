
#include "net.hpp"

using namespace chrono;

int main() {

  vector< ImageServerConf > servers;
  servers.emplace_back("localhost", "2204", 10.0);
  servers.emplace_back("localhost", "2205", 10.0);
  ImageMultiClient client(servers);

  while (true) {
    while (true) {
      auto res = client.advance_to_stream(0, false);
      if (res.size() == 0) break;
    }
    client.print_status();
    this_thread::sleep_for(milliseconds(300));
  }

  return 0;

}
