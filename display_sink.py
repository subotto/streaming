#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import struct
import pygame
import pygame.locals
import numpy
import datetime
import tzlocal

from imgio import decode_jpeg_data, read_jpeg_frame, TJPF_RGBX

MODE_STOP = 0
MODE_SINGLE = 1
MODE_PLAYING = 2
MODE_PLAYING_BACKWARD = 3

def goto(new_num):
    global num, fin, frame_pos
    if num == new_num:
        return
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
    imdata = None
    timestamp = None
    font = pygame.font.SysFont('Inconsolata', 16)
    skip = 1

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
                        if mode == MODE_PLAYING:
                            mode = MODE_STOP
                        else:
                            mode = MODE_PLAYING

                    elif event.unicode == u'b':
                        if mode == MODE_PLAYING_BACKWARD:
                            mode = MODE_STOP
                        else:
                            mode = MODE_PLAYING_BACKWARD

                    elif event.unicode == u'n':
                        skip = 1

                    elif event.unicode == u'm':
                        skip += 1

                    elif event.unicode == u'b':
                        skip = max(1, skip - 1)

                    elif event.unicode == u'd':
                        if imdata is not None:
                            filename = datetime.datetime.now().strftime("frame-%Y%m%d-%H%M%S-%%f.jpeg") % (timestamp)
                            print >> sys.stderr, "Dumping frame on %s" % (filename)
                            fout = open(filename, 'w')
                            fout.write(imdata)
                            fout.close()

            if mode in [MODE_SINGLE, MODE_PLAYING, MODE_PLAYING_BACKWARD]:
                imdata, timestamp = read_jpeg_frame(fin)
                if imdata is None:
                    mode = MODE_STOP
                    image = None
                else:
                    image = decode_jpeg_data(imdata, pixel_format=TJPF_RGBX)
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
                    writing_pos = (0, 0)
                    font_surf = font.render("Timestamp: %f" % (timestamp), True, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                    font_surf = font.render("Time: %s" % (datetime.datetime.fromtimestamp(timestamp, tz=tzlocal.get_localzone())), True, pygame.Color(255, 255, 255), pygame.Color(0, 0, 0))
                    surf.blit(font_surf, writing_pos)
                    writing_pos = (writing_pos[0], writing_pos[1] + font_surf.get_size()[1])
                    pygame.display.flip()

                    if mode == MODE_SINGLE:
                        mode = MODE_STOP
                        goto(num - 1)

                    if mode == MODE_PLAYING:
                        goto(num - 1 + skip)

                    if mode == MODE_PLAYING_BACKWARD:
                        goto(num - 1 - skip)
                        if num == 0:
                            mode = MODE_SINGLE

            clock.tick(30)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
