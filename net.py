#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Queue
import SocketServer
import threading

QUEUE_MAXSIZE = 5 * 120


class ImageSocketServerHandler:

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
                self.socket.sendall(data)
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


class ImageSocketServer:

    def __init__(self, host, port):
        self.server = SocketServer.ThreadingTCPServer((host, port), ImageSocketServerRequest)
        self.handlers = []

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
