
#ifndef NET_HPP
#define NET_HPP

#include <string>
#include <vector>
#include <thread>
#include <deque>
#include <mutex>
#include <condition_variable>

#include "imgio.h"

using namespace std;

struct ImageServerConf {
  string host;
  string port;
  double timeout;

  ImageServerConf(string host, string port, double timeout);
};

typedef enum {
  IM_OP_RAW,
  IM_OP_DECODE,
  IM_OP_YUV_DECODE
} ImageOp;

class ImageMultiClient {
private:
  vector< ImageServerConf > servers;
  vector< deque< Image* > > queues;
  vector< thread > threads;
  vector< long > mem_usage;
  mutex queues_mutex;
  recursive_mutex advance_mutex;
  condition_variable queues_condition;
  ImageOp op;
  volatile bool running;

public:
  ImageMultiClient(const vector< ImageServerConf > &servers, ImageOp op=IM_OP_DECODE);
  ~ImageMultiClient();
  void worker(int shard);
  vector< const Image* > advance_to_timestamp(double timestamp, bool block=false, bool empty=false);
  vector< const Image* > advance_to_stream(int shard, bool block=false, bool empty=false);
  vector< const Image* > advance_to_last(bool block=false, bool empty=false);
  vector< tuple< double, int, int > > get_status();
  void print_status();
  void stop();
};

#endif
