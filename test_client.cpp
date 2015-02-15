
#include "net.hpp"

using namespace chrono;

int main() {

  vector< ImageServerConf > servers;
  servers.emplace_back("localhost", "2204", 2.0);
  servers.emplace_back("localhost", "2205", 2.0);
  ImageMultiClient client(servers);

  while (true) {
    while (true) {
      auto res = client.advance_to_stream(0, false);
      if (res.size() == 0) break;
      else {
        for (auto &r : res) {
          fprintf(stderr, "%f  ", r->timestamp);
        }
        fprintf(stderr, "\n");
      }
    }
    client.print_status();
    this_thread::sleep_for(milliseconds(300));
  }

  return 0;

}
