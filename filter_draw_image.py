#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo
import rsvg
import math

import base64

from imgio import read_frame, write_frame, get_cairo_context, get_cairo_image, read_raw_frame, swap_channels, read_base64_blob_from_phantom, cv2_open_from_data, image_from_string

#sheep_svg = rsvg.Handle("pecora.svg")
fweb = open("webpage_fifo", "r")

def edit_frame(ctx, size, timestamp):
    global fweb
    #image_to_draw = swap_channels(read_raw_frame(fweb, 1280, 720))
    #image_to_draw = cv2_open_from_data(base64.b64decode(read_base64_blob_from_phantom(fweb)))
    imdata, timestamp = read_jpeg_frame(fweb)
    assert len(imdata) == 4 * size[0] * size[1], "Image from Phantom has wrong size"
    image_to_draw = image_from_string(imdata)
    _, web_render = get_cairo_image(swap_channels(image_to_draw))
    ctx.save()
    ctx.set_source_surface(web_render)
    ctx.paint()
    ctx.restore()

def main():
    #fweb = open("webpage_fifo", "r")
    try:
        while True:
            image, timestamp = read_frame(sys.stdin)
            #print >> sys.stderr, image.shape
            ctx, size, surf = get_cairo_context(image)
            edit_frame(ctx, size, timestamp)
            surf.flush()
            write_frame(sys.stdout, image, timestamp)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
