
#include "net.hpp"

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <netdb.h>
#include <unistd.h>
#include <assert.h>

using namespace chrono;

ImageServerConf::ImageServerConf(string host, string port, double timeout)
  : host(host), port(port), timeout(timeout) {

}

ImageMultiClient::ImageMultiClient(const vector< ImageServerConf > &servers, ImageOp op)
  : servers(servers), op(op), running(true) {

  // Allocate queues and start threads; threads vector is initially
  // resized in order to be sure that no threads will access it while
  // it is being rehashed
  this->queues.resize(servers.size());
  this->mem_usage.resize(servers.size());
  this->threads.resize(servers.size());
  for (unsigned int i = 0; i < servers.size(); i++) {
    this->threads[i] = thread(&ImageMultiClient::worker, this, i);
  }

}

ImageMultiClient::~ImageMultiClient() {

  this->stop();
  for (auto &thread : this->threads) {
    thread.join();
  }

}

void ImageMultiClient::worker(int shard) {

  int sd = -1;
  TJContext *ctx = NULL;
  struct addrinfo *res = NULL;
  int succeed;
  struct addrinfo hints;
  FILE *fin;

  // Create TJContext
  ctx = create_tjcontext();
  if (ctx == NULL) {
    fprintf(stderr, "Worker %d, could not create TJContext", shard);
    goto cleanup;
  }

  // Resolve network name
  bzero(&hints, sizeof(struct addrinfo));
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;
  succeed = getaddrinfo(this->servers[shard].host.c_str(), this->servers[shard].port.c_str(), &hints, &res);
  if (succeed != 0) {
    fprintf(stderr, "Worker %d, could not resolve network name: %s", shard, gai_strerror(succeed));
    goto cleanup;
  }

  // Create the socket
  sd = socket(AF_INET, SOCK_STREAM, 0);
  if (sd < 0) {
    fprintf(stderr, "Worker %d, could not create socket: %s", shard, strerror(errno));
    goto cleanup;
  }

  // Connect the socket
  succeed = connect(sd, res->ai_addr, res->ai_addrlen);
  if (succeed < 0) {
    fprintf(stderr, "Worker %d, could not connect socket: %s", shard, strerror(errno));
    goto cleanup;
  }

  // Create the C-style file
  fin = fdopen(sd, "r");
  if (fin == NULL) {
    fprintf(stderr, "Worker %d, could not open file from socket: %s", shard, strerror(errno));
    goto cleanup;
  }

  while (this->running) {
    // Take an image
    Image *image;
    if (this->op == IM_OP_DECODE) image = read_frame(ctx, fin);
    else if (this->op == IM_OP_RAW) image = read_jpeg_frame(ctx, fin);
    else if (this->op == IM_OP_YUV_DECODE) image = read_frame_to_yuv(ctx, fin);
    else assert(false);
    if (image == NULL) {
      fprintf(stderr, "Worker %d, could not read image (socket was probably closed)", shard);
      goto cleanup;
    }

    // Take the lock on queues and push the image to the right queue
    unique_lock< mutex > lock(this->queues_mutex);
    this->queues[shard].push_back(image);
    lock.unlock();

    // Update memory usage
    struct rusage resources;
    getrusage(RUSAGE_THREAD, &resources);
    this->mem_usage[shard] = resources.ru_maxrss;

    // Then notify the waiting threads
    this->queues_condition.notify_all();
  }

 cleanup:
  if (sd >= 0) {
    succeed = close(sd);
    if (succeed < 0) {
      fprintf(stderr, "Worker %d, could not close socket: %s (but I do not know what to do about that...)", shard, strerror(errno));
    }
  }
  free(res);
  free_tjcontext(ctx);

}

vector< const Image* > ImageMultiClient::advance_to_timestamp(double timestamp, bool block, bool empty) {

  // Acquire both locks (so that worker() is permitted to make
  // progress when advance_to_*() is waiting; but two calls to
  // advance_to_*() are never concurrently allowed)
  unique_lock< recursive_mutex > adv_lock(this->advance_mutex);
  unique_lock< mutex > lock(this->queues_mutex);

  // Trim queues and check if we have to wait for frames
  bool waiting = false;
  do {
    for (unsigned int i = 0; i < this->queues.size(); i++) {
      auto &queue = this->queues[i];

      // Trim the queue
      while (true) {
        if (queue.size() == 1 && !empty) break;
        if (queue.size() == 0) break;
        Image *first = *queue.begin();
        if (first->timestamp < timestamp) {
          free_image(first);
          queue.pop_front();
        } else {
          break;
        }
      }

      // Check whether the queue needs to be waiting for frames: we
      // need to wait if (after trimming) we have exactly one frame in
      // the queue and its timestamp is not too old (i.e., greater
      // than reference timestamp minus the queue timeout) and is not
      // greater than reference timestamp
      if (queue.size() == 1 && (*queue.begin())->timestamp >= timestamp - this->servers[i].timeout && (*queue.begin())->timestamp < timestamp) {
        waiting = true;
      }
    }

    // If we have to wait, let us block or return
    if (waiting) {
      if (!block) {
        return vector< const Image * >();
      } else {
        this->queues_condition.wait(lock);
      }
    }
  } while (waiting);

  // Build and return frames
  vector< const Image* > ret;
  for (auto it = this->queues.begin(); it != this->queues.end(); it++) {
    auto &queue = *it;
    if (queue.size() == 0) ret.push_back(NULL);
    else ret.push_back(*queue.begin());
  }

  return ret;

}

vector< const Image* > ImageMultiClient::advance_to_stream(int shard, bool block, bool empty) {

  // Acquire both locks (see advance_to_timestamp())
  unique_lock< recursive_mutex > adv_lock(this->advance_mutex);
  unique_lock< mutex > lock(this->queues_mutex);

  auto &primary = this->queues[shard];

  // If blocking, wait to have at least two frames in primary queue
  if (block) {
    while (primary.size() < 2) {
      this->queues_condition.wait(lock);
    }
  }

  // Check the timestamp of the second frame
  double timestamp;
  if (primary.size() >= 2) {
    timestamp = (*(++primary.begin()))->timestamp;
  } else {
    return vector< const Image * >();
  }

  // Unlock before entering advance_to_timestamp(), otherwise it would
  // deadlock
  lock.unlock();

  return advance_to_timestamp(timestamp, block, empty);

}

vector< const Image* > ImageMultiClient::advance_to_last(bool block, bool empty) {

  // Acquire both locks (see advance_to_timestamp())
  unique_lock< recursive_mutex > adv_lock(this->advance_mutex);
  unique_lock< mutex > lock(this->queues_mutex);

  double timestamp = 1e20;
  for (auto &queue : this->queues) {
    if (queue.size() > 0) {
      timestamp = min(timestamp, (*(--queue.end()))->timestamp);
    }
  }

  // Unlock before entering advance_to_timestamp(), otherwise it would
  // deadlock
  lock.unlock();

  return advance_to_timestamp(timestamp, block, empty);

}

vector< tuple< double, int, int > > ImageMultiClient::get_status() {

  unique_lock< mutex > lock(this->queues_mutex);
  double now = duration_cast< duration< double > >(system_clock::now().time_since_epoch()).count();

  vector< tuple< double, int, int > > ret;
  for (unsigned int i = 0; i < this->queues.size(); i++) {
    auto &queue = this->queues[i];
    double time_delta;
    if (queue.size() > 0) time_delta = now - (*(--queue.end()))->timestamp;
    else time_delta = -100.0;
    ret.push_back(make_tuple(time_delta, queue.size(), this->mem_usage[i]));
  }
  return ret;

}

void ImageMultiClient::print_status() {

  auto status = this->get_status();
  for (auto &s : status) {
    fprintf(stderr, "%f %d %d     ", get<0>(s), get<1>(s), get<2>(s));
  }
  fprintf(stderr, "\n");
  fflush(stderr);

}

void ImageMultiClient::stop() {

  this->running = false;

}
