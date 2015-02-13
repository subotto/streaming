#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Queue
import collections
import SocketServer
import threading
import socket
import time
import resource

from imgio import read_frame, write_frame, read_jpeg_frame

QUEUE_MAXSIZE = 5 * 30


def clear_line():
    sys.stderr.write('\r\033[2K')


class ImageSocketServerHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # When beginning execution, register itself against the
        # ImageSocketServer
        self.queue = Queue.Queue(maxsize=QUEUE_MAXSIZE)
        self.thread = threading.current_thread()
        self.server.register_handler(self)
        self.name = "%s %s" % self.client_address

        print >> sys.stderr, "Start sending data to %s" % (self.name)

        # Then keep waiting for data and writing it to the socket
        try:
            while True:
                data = self.queue.get(block=True)
                self.request.sendall(data)
                # There apparently is no mechanism to flush the socket
                self.queue.task_done()

        except:
            print >> sys.stderr, "Exception while sending data to %s" % (self.name)

        print >> sys.stderr, "Finished sending data to %s" % (self.name)

    def finish(self):
        self.request.close()

    def post_data(self, data):
        # If the thread is dead, return False, so that the
        # ImageSocketServer stops sending data and performs cleanup
        if not self.thread.is_alive():
            return False

        # Else, enqueue the new data payload
        try:
            self.queue.put(data, block=False)
        except Queue.Full:
            print >> sys.stderr, "Frame lost when queueing for %s" % (self.name)

        return True


class ImageSocketServer(SocketServer.ThreadingTCPServer):

    def __init__(self, host, port):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), ImageSocketServerHandler)

        self.handlers = []
        self.daemon_threads = True
        self.main_thread = threading.Thread(target=self.serve_forever)
        self.main_thread.daemon = True
        self.main_thread.start()

    def register_handler(self, handler):
        self.handlers.append(handler)

    def post_data(self, data):
        # Pass the payload to all handlers
        to_remove = []
        for handler in self.handlers:
            alive = handler.post_data(data)
            if not alive:
                to_remove.append(handler)

        # Remove all handlers that have died (FIXME: this could be
        # more efficient)
        for handler in to_remove:
            self.handlers.remove(handler)


class ImageMultiClient:

    def __init__(self, servers):
        """Connect to a number of image servers.

        The parameter servers is a list of tuples of the type ((host,
        port), timeout). Timeout is a float value that specifies the
        maximum number of seconds frames getting in can delay behind
        real time.

        """
        # Lay out arguments in internal structures
        self.addresses = []
        self.timeouts = []
        for i, (address, timeout) in enumerate(servers):
            self.addresses.append(address)
            self.timeouts.append(timeout)

        # Individual frame queues and threads
        self.queues = [collections.deque() for _ in servers]
        self.threads = []

        # Every time a thread has a new frame, it notifies this
        # condition variable
        self.condition = threading.Condition()

        # Debugging and profiling
        self.memory_used = [None] * len(servers)

        # Set up and spawn threads
        for i, _ in enumerate(servers):
            thread = threading.Thread(target=self.worker, args=[i])
            thread.daemon = True
            self.threads.append(thread)
        for thread in self.threads:
            thread.start()

    def get_status(self):
        now = time.time()
        ret = []
        for queue, memory in zip(self.queues, self.memory_used):
            delay = None
            if len(queue) != 0:
                # [last item][timestamp]
                delay = now - queue[-1][1]
            ret.append((delay, len(queue), memory))
        return ret

    def write_status(self):
        status = self.get_status()
        clear_line()
        sys.stderr.write(("%40s " * len(status)) % tuple(status))

    def worker(self, shard):
        # Set up the connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.addresses[shard])
        fin = sock.makefile()

        # Start receiving frames
        while True:
            image, timestamp = read_frame(fin)
            with self.condition:
                self.queues[shard].append((image, timestamp))
                self.condition.notifyAll()
            # RUSAGE_THREAD is not mapped in resource module, but
            # direct inspection of Linux headers shows it is 1
            self.memory_used[shard] = resource.getrusage(1).ru_maxrss / 1000

    def advance_to_timestamp(self, timestamp, empty=False):
        """Pop all elements with timestamp strictly smaller than the specified
        one, from all queues. As an exception, if empty is False then
        queues are never emptied; i.e., last item never gets deleted,
        even when it has past timestamp.

        """
        with self.condition:
            # Trim queues
            for queue in self.queues:
                while True:
                    if len(queue) == 1 and not empty:
                        break
                    try:
                        first = queue[0]
                    except IndexError:
                        break
                    # [timestamp]
                    if first[1] < timestamp:
                        queue.popleft()
                    else:
                        break

            # Build and return frames
            ret = []
            for queue in self.queues:
                if len(queue) == 0:
                    ret.append(None)
                else:
                    ret.append(queue[0])
            return ret

    def advance_to_stream(self, shard, block=False, empty=False):
        with self.condition:
            queue = self.queues[shard]

            # Discard first frame if there is one, so that we do not
            # go over the same frame over and over
            if len(queue) > 0:
                queue.popleft()

            # If blocking, wait to have another frame
            if block:
                while True:
                    if len(queue) > 0:
                        break
                    else:
                        self.condition.wait()

            # Check if there is a new frame (there is one for sure if
            # we were blocking)
            try:
                # [shard][first element][timestamp]
                timestamp = queue[0][1]
            except IndexError:
                return None

            # If there is, proceed with advancing
            return self.advance_to_timestamp(timestamp, empty=empty)


class WritingThread:
    """A simplified and non-socket-bound version of the classes
    above. Instead of writing data to a file, you pass them to a
    thread that writes to the file. The main program is not blocked by
    writing to the file.

    Just for testing.

    """

    def __init__(self, fout):
        self.fout = fout
        self.thread = threading.Thread(target=self.work)
        self.thread.daemon = True
        self.queue = Queue.Queue(maxsize=QUEUE_MAXSIZE)
        self.active = True

        self.thread.start()

    def work(self):
        try:
            while True:
                data = self.queue.get(block=True)
                self.fout.write(data)
                #self.fout.flush()
                self.queue.task_done()

        except:
            self.active = False
            raise

    def post_data(self, data):
        if not self.active:
            return False

        try:
            self.queue.put(data, block=False)
        except Queue.Full:
            print >> sys.stderr, "Frame lost when queueing"

        return True

    def write(self, data):
        self.post_data(data)
