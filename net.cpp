
#include "net.hpp"

#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

ImageMultiClient::ImageMultiClient(const vector< ImageServerConf > &servers)
  : servers(servers), running(true) {

  // Allocate queues and start threads; threads vector is initially
  // resized in order to be sure that no threads will access it while
  // it is being rehashed
  this->queues.resize(servers.size());
  this->threads.resize(servers.size());
  for (int i = 0; i < servers.size(); i++) {
    this->threads.emplace_back(&ImageMultiClient::worker, this, i);
  }

}

void ImageMultiClient::worker(int shard) {

  // Resolve network name
  struct addrinfo hints = { 0 };  // FIXME: can the initializer be eliminated?
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;
  struct addrinfo *res;
  struct addrinfo to_connect;
  int succeed = getaddrinfo(this->servers[shard].host.c_str(), this->servers[shard].port.c_str(), &hints, &res);
  if (succeed != 0) {
    freeaddrinfo(res);
    fprintf(stderr, "Worker %d, could not resolve network name: %s", shard, gai_strerror(succeed));
    return;
  }
  to_connect = *res;
  freeaddrinfo(res);

  // Create the socket
  int sd;
  sd = socket(AF_INET, SOCK_STREAM, 0);
  if (sd < 0) {
    fprintf(stderr, "Worker %d, could not create socket: %s", shard, strerror(errno));
    return;
  }

  // Connect the socket
  succeed = connect(sd, to_connect.ai_addr, to_connect.ai_addrlen);
  if (succeed < 0) {
    fprintf(stderr, "Worker %d, could not connect socket: %s", shard, strerror(errno));
    return;
  }

  while (this->running) {

  }

}
