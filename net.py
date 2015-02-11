#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Queue
import SocketServer
import threading
import socket

from imgio import read_frame, write_frame

QUEUE_MAXSIZE = 5 * 120


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


# TODO: finish
class ImageMultiClient:

    def __init__(self, servers):
        self.addresses = []
        self.timeouts = []
        for i, (address, timeout) in enumerate(server):
            self.addresses[i] = addres
            self.timeouts[i] = timeout
        self.queues = [Queue.Queue() for _ in self.servers]
        self.threads = []
        self.condition = None  # TODO
        for i, _ in enumerate(self.servers):
            thread = threading.Thread(target=worker, args=[i])
            thread.daemon = True
            self.threads.append(thread)
        for thread in threads:
            thread.start()

    def worker(self, shard):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.addresses[shard])
        fin = sock.makefile()
        while True:
            image, timestamp = read_frame(fin)
            self.queue.put((image, timestamp))


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
