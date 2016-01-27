#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import struct
import pygame
import pygame.locals
import numpy

from imgio import read_frame, read_jpeg_frame, TJPF_RGBX

MODE_STOP = 0
MODE_SINGLE = 1
MODE_PLAYING = 2
MODE_PLAYING_BACKWARD = 3

def goto(new_num):
    global num, fin, frame_pos
    if new_num < 0:
        new_num = 0
    if new_num < len(frame_pos):
        num = new_num
        fin.seek(frame_pos[num])
    else:
        num = len(frame_pos) - 1
        fin.seek(frame_pos[num])
        while num < new_num:
            imdata, timestamp = read_jpeg_frame(fin)
            if imdata is None:
                return
            num += 1
            frame_pos.append(fin.tell())

def main():
    global num, fin, frame_pos
    # Init PyGame
    fin_name = sys.argv[1]
    size = map(int, sys.argv[2:4])
    pygame.init()
    pygame.display.set_caption('display_sink.py')
    surf = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)

    if fin_name == '-':
        fin = sys.stdin
    else:
        fin = open(fin_name)
    seekable = True
    frame_pos = [0]
    try:
        fin.seek(0)
    except IOError:
        seekable = False
    mode = MODE_PLAYING
    num = 0

    clock = pygame.time.Clock()
    image = None

    try:
        while True:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_ESCAPE or event.unicode == u'q':
                        pygame.event.post(pygame.event.Event(pygame.locals.QUIT))

                    elif event.unicode == u'.':
                        mode = MODE_SINGLE
                        goto(num + 1)

                    elif event.unicode == u',':
                        mode = MODE_SINGLE
                        goto(num - 1)

                    elif event.unicode == u' ':
                        mode = MODE_PLAYING

                    elif event.unicode == u'b':
                        mode = MODE_PLAYING_BACKWARD

            if mode in [MODE_SINGLE, MODE_PLAYING, MODE_PLAYING_BACKWARD]:
                image, timestamp = read_frame(fin, pixel_format=TJPF_RGBX)
                if image is None:
                    mode = MODE_STOP
                else:
                    num += 1
                    if seekable:
                        if num == len(frame_pos):
                            frame_pos.append(fin.tell())
                        else:
                            assert num < len(frame_pos)
                            assert fin.tell() == frame_pos[num]
                    #print type(image)
                    image_size = image.shape[1], image.shape[0]
                    #print image_size
                    pygame_image = pygame.image.fromstring(image.tostring(), image_size, 'RGBX')
                    surf.blit(pygame_image, (0, 0))
                    pygame.display.flip()

                    if mode == MODE_SINGLE:
                        mode = MODE_STOP
                        goto(num - 1)

                    if mode == MODE_PLAYING_BACKWARD:
                        goto(num - 2)
                        if num == 0:
                            mode = MODE_SINGLE

            clock.tick(30)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
