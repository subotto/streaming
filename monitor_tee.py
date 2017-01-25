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
import traceback
import tzlocal
import collections

from imgio import read_jpeg_frame, write_jpeg_frame, decode_jpeg_data, TJPF_RGBX

QUEUE_MAXSIZE = 500
HOST = "localhost"
PORT = 2204
#CUT_EVERY = datetime.timedelta(seconds=10)
CUT_EVERY = datetime.timedelta(minutes=3)

last_frame = None, None
fin = None
fouts_lock = threading.Lock()
fouts = []
finish = False
connections_lock = threading.Lock()
connections = []

class FPSEstimator:
    def __init__(self, span):
        self.queue = collections.deque()
        self.length = 0
        self.span = span
        self.lock = threading.Lock()

    def push_frame(self, timestamp):
        with self.lock:
            self.queue.append(timestamp)
            self.length += 1

            while self.queue[0] < timestamp - self.span:
                self.queue.popleft()
                self.length -= 1

            return float(self.length) / self.span

    def get_fps(self):
        with self.lock:
            return float(self.length) / self.span

fps_est = FPSEstimator(5.0)

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
            if timestamp is not None:
                fps_est.push_frame(timestamp)
            last_frame = (imdata, timestamp)
            with fouts_lock:
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
    font = pygame.font.SysFont('Inconsolata', 16)

    fin = sys.stdin
    fouts = []
    copy_thread = threading.Thread(target=copy)
    copy_thread.start()

    recording = False

    # Initialize ConnectionServer
    server = ThreadedTCPServer((HOST, PORT), Connection)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    recording_began = None
    filename = None

    try:
        while not finish:
            # Process events
            toggle_recording = False
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    finish = True

                elif event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.locals.QUIT))

                    if event.unicode == 'r':
                        toggle_recording = True

            now = datetime.datetime.now()
            stop_recording = False
            start_recording = False
            if toggle_recording:
                if recording:
                    stop_recording = True
                else:
                    start_recording = True

            else:
                if recording and now >= recording_began + CUT_EVERY:
                    stop_recording = True
                    start_recording = True

            with fouts_lock:
                if stop_recording:
                    print >> sys.stderr, "Closing record file"
                    fouts[-1].close()
                    del fouts[-1]
                    recording = False
                    filename = None
                    recording_began = None
                if start_recording:
                    recording_began = datetime.datetime.now()
                    filename = recording_began.strftime("record-%Y%m%d-%H%M%S.gjpeg")
                    print >> sys.stderr, "Recording on %s" % (filename)
                    fout = open(filename, 'w')
                    fouts.append(fout)
                    recording = True

            # Read image and show it (TODO - I couldn't make any sense
            # of the surfarray interface, which in theory should be
            # the best way to do these things)
            if last_frame[0] is not None:
                try:
                    #print >> sys.stderr, "Frame received"
                    imdata, timestamp = last_frame
                    image = decode_jpeg_data(imdata, pixel_format=TJPF_RGBX)
                    image_size = image.shape[1], image.shape[0]
                    pygame_image = pygame.image.fromstring(image.tostring(), image_size, 'RGBX')
                    surf.blit(pygame_image, (0, 0))
                    writing_pos = (0, 0)
                    font_surf = font.render("Recording on file %s" % (filename) if recording else "Not recording", True, pygame.Color(255, 0, 0) if recording else pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                    font_surf = font.render("Timestamp: %f" % (timestamp), True, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                    font_surf = font.render("Time: %s" % (datetime.datetime.fromtimestamp(timestamp, tz=tzlocal.get_localzone())), True, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                    font_surf = font.render("Real FPS: %f" % (fps_est.get_fps()), True, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                    font_surf = font.render("Visualization FPS: %f" % (clock.get_fps()), True, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                except:
                    print >> sys.stderr, "Exception while showing the JPEG frame"
                    traceback.print_exc(file=sys.stderr)

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
