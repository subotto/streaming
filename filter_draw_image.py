#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo
import rsvg
import math

import base64

from imgio import read_frame, write_frame, get_cairo_context, get_cairo_image, read_raw_frame, swap_channels, read_blob_from_phantom, cv2_open_from_data

#sheep_svg = rsvg.Handle("pecora.svg")
fweb = open("webpage_fifo", "r")

def edit_frame(ctx, size, num):
    global fweb
    #image_to_draw = read_frame(fweb)
    #image_to_draw = swap_channels(read_raw_frame(fweb, 1280, 720))
    #image_to_draw = cairo.ImageSurface.create_from_png("webpage_render.png")
    image_to_draw = cv2_open_from_data(base64.b64decode(read_blob_from_phantom(fweb)))
    _, web_render = get_cairo_image(swap_channels(image_to_draw))
    ctx.save()
    ctx.set_source_surface(web_render)
    ctx.paint()
    ctx.restore()
    
def main():
    #fweb = open("webpage_fifo", "r")
    num = 0
    try:
        while True:
            image = read_frame(sys.stdin)
            
            #print >> sys.stderr, image.shape
            ctx, size, surf = get_cairo_context(image)
            edit_frame(ctx, size, num)
            surf.flush()
            write_frame(sys.stdout, image)
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
