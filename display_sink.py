#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import pygame
import pygame.locals
import numpy

from imgio import read_frame, TJPF_RGBX

def main():
    # Init PyGame
    size = map(int, sys.argv[1:3])
    pygame.init()
    pygame.display.set_caption('display_sink.py')
    surf = pygame.display.set_mode(size, pygame.DOUBLEBUF, 32)

    num = 0
    try:
        while True:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.locals.QUIT))

            # Read image and show it (TODO - I couldn't make any sense
            # of the surfarray interface, which in theory should be
            # the best way to do these things)
            image, timestamp = read_frame(sys.stdin, pixel_format=TJPF_RGBX)
            #print type(image)
            image_size = image.shape[1], image.shape[0]
            #print image_size
            pygame_image = pygame.image.fromstring(image.tostring(), image_size, 'RGBX')
            surf.blit(pygame_image, (0, 0))

            pygame.display.flip()
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
