#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import pygame
import pygame.locals
import numpy
import threading
import datetime

from imgio import read_jpeg_frame, write_jpeg_frame, decode_jpeg_data, TJPF_RGBX

last_frame = None
fin = None
fouts = []
finish = False

def copy():
    global fin, fouts, finish, last_frame
    try:
        while not finish:
            imdata, timestamp = read_jpeg_frame(fin)
            last_frame = (imdata, timestamp)
            for fout in fouts:
                write_jpeg_frame(fout, imdata, timestamp)
    except KeyboardInterrupt:
        pass
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
    fouts = [sys.stdout]
    copy_thread = threading.Thread(target=copy)
    copy_thread.start()

    recording = False

    try:
        while not finish:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    pygame.quit()
                    sys.exit()

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
                            del fouts[1]
                            recording = False

            # Read image and show it (TODO - I couldn't make any sense
            # of the surfarray interface, which in theory should be
            # the best way to do these things)
            if last_frame is not None:
                print "Frame received"
                imdata, timestamp = last_frame
                image = decode_jpeg_data(imdata, pixel_format=TJPF_RGBX)
                #print type(image)
                image_size = image.shape[1], image.shape[0]
                #print image_size
                pygame_image = pygame.image.fromstring(image.tostring(), image_size, 'RGBX')
                surf.blit(pygame_image, (0, 0))

            pygame.display.flip()
            clock.tick(15)

    except KeyboardInterrupt:
        pass
    finally:
        finish = True

if __name__ == '__main__':
    main()
