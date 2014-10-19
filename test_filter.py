#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo
import rsvg
import math

from imgio import read_frame, write_frame, get_cairo_context, TJPF_BGRX

#sheep_svg = rsvg.Handle("pecora.svg")

fin = open('webpage_fifo', 'r')

def read_svg_frame():
    global fin
    length=int(fin.readline().strip())
    #length, = struct.unpack("!I", length_tag)
    #print >> sys.stderr, "length ",length
    return fin.read(length+1)

def edit_frame(ctx, size, num):
 #   ctx.scale (size[0]/4, size[1]/3)
 #   ctx.set_source_rgb(0.0, 1.0, 0.0)
 #   ctx.select_font_face("Ubuntu Medium",
 #                        cairo.FONT_SLANT_NORMAL,
 #                        cairo.FONT_WEIGHT_NORMAL)
 #   ctx.set_font_size(0.12)
 #   text = "MATEMATICI 1874 1110 FISICI"
 #   x_bearing, y_bearing, width, height = ctx.text_extents(text)[:4]
 #   # ctx.move_to(0.5 - width / 2 - x_bearing, 0.5 - height / 2 - y_bearing)
 #   ctx.move_to(0.1, 0.1 - y_bearing)
 #   ctx.show_text(text)

    ctx.move_to(0.1, 0.1)
    ctx.identity_matrix()
 
 #   ctx.translate(2.0 * num, 350.0 + 50.0 * math.cos(2 * math.pi * num / 200.0))
 #   ctx.scale(0.25, 0.25)
    
    svg_code=read_svg_frame()
    #print >> sys.stderr, svg_code
    svg_handle = rsvg.Handle(data=svg_code)
    #svg_handle.write(buffer=svg_code)
    
    #svg_handle = rsvg.Handle('images/4gears.svg')
    
    svg_handle.render_cairo(ctx)

def main():
    num = 0
    try:
        while True:
            image = read_frame(sys.stdin, pixel_format=TJPF_BGRX)
            #print >> sys.stderr, image.shape
            ctx, size, surf = get_cairo_context(image)
            edit_frame(ctx, size, num)
            surf.flush()
            write_frame(sys.stdout, image, pixel_format=TJPF_BGRX)
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
