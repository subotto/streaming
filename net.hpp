
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
};

class ImageMultiClient {
private:
  vector< ImageServerConf > servers;
  vector< deque< Image > > queues;
  vector< thread > threads;
  mutex queues_mutex;
  condition_variable queues_condition;
  volatile bool running;

public:
  ImageMultiClient(const vector< ImageServerConf > &servers);
  void worker(int shard);
};

#endif
