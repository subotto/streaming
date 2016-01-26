#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import struct
import pygame
import pygame.locals
import numpy
import threading
import datetime
import socket
import SocketServer
import Queue
import time

from imgio import read_jpeg_frame, write_jpeg_frame, decode_jpeg_data, TJPF_RGBX

QUEUE_MAXSIZE = 100
HOST = "localhost"
PORT = 2204

last_frame = None
fin = None
fouts = []
finish = False
connections_lock = threading.Lock()
connections = []

# From https://docs.python.org/2/library/socketserver.html#asynchronous-mixins
class Connection(SocketServer.BaseRequestHandler):
    def handle(self):
        print >> sys.stderr, "New connection"
        # We will never read from the socket, so we shut it down
        # immediately for reading
        self.request.shutdown(socket.SHUT_RD)
        self.queue = Queue.Queue(QUEUE_MAXSIZE)
        fd = self.request.makefile('w')
        try:
            with connections_lock:
                connections.append(self)
            while not finish:
                imdata, timestamp = self.queue.get(block=True)
                write_jpeg_frame(fd, imdata, timestamp)
                fd.flush()
        finally:
            with connections_lock:
                connections.remove(self)
            print >> sys.stderr, "Connection closed"
            fd.close()
            self.request.shutdown(socket.SHUT_WR)

    def enqueue_frame(self, imdata, timestamp):
        try:
            self.queue.put((imdata, timestamp), block=False)
            return True
        except Queue.Full:
            print >> sys.stderr, "Discarding frame because of a full queue"
            return False

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def copy():
    global fin, fouts, finish, last_frame
    try:
        while not finish:
            imdata, timestamp = read_jpeg_frame(fin)
            last_frame = (imdata, timestamp)
            for fout in fouts:
                write_jpeg_frame(fout, imdata, timestamp)
            with connections_lock:
                for connection in connections:
                    connection.enqueue_frame(imdata, timestamp)
            time.sleep(0)
    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupt received in copy thread"
    finally:
        finish = True

def main():
    global fin, fouts, finish, last_frame
    # Init PyGame
    size = map(int, sys.argv[1:3])
    pygame.init()
    pygame.display.set_caption(sys.argv[0])
    surf = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)
    clock = pygame.time.Clock()

    fin = sys.stdin
    fouts = []
    copy_thread = threading.Thread(target=copy)
    copy_thread.start()

    recording = False

    # Initialize ConnectionServer
    server = ThreadedTCPServer((HOST, PORT), Connection)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    try:
        while not finish:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    finish = True

                elif event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.locals.QUIT))

                    if event.unicode == 'r':
                        if not recording:
                            filename = datetime.datetime.now().strftime("record-%Y%m%d-%H%M%S.gjpeg")
                            print >> sys.stderr, "Recording on %s" % (filename)
                            fout = open(filename, 'w')
                            fouts.append(fout)
                            recording = True
                        else:
                            print >> sys.stderr, "Closing record file"
                            del fouts[-1]
                            recording = False

            # Read image and show it (TODO - I couldn't make any sense
            # of the surfarray interface, which in theory should be
            # the best way to do these things)
            if last_frame is not None:
                #print >> sys.stderr, "Frame received"
                imdata, timestamp = last_frame
                image = decode_jpeg_data(imdata, pixel_format=TJPF_RGBX)
                image_size = image.shape[1], image.shape[0]
                pygame_image = pygame.image.fromstring(image.tostring(), image_size, 'RGBX')
                surf.blit(pygame_image, (0, 0))

            pygame.display.flip()
            clock.tick(15)

    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupt received in main thread"
    finally:
        finish = True
        pygame.quit()

    print >> sys.stderr, "Shutting down server"
    server.shutdown()
    server.server_close()

    print >> sys.stderr, "Joining on the server thread"
    server_thread.join()
    print >> sys.stderr, "Joining on the copy thread"
    copy_thread.join()
    print >> sys.stderr, "Main thread quitting"

if __name__ == '__main__':
    main()
