#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo
import rsvg
import math
import time

from imgio import read_frame, write_frame, get_cairo_context, TJPF_BGRX

class Clock:

    def __init__(self):
        self.time = time.time()

    def tic(self, desc=""):
        new_time = time.time()
        print >> sys.stderr, "> TIC! %f (%s)" % (new_time - self.time, desc)
        self.time = new_time

clock = Clock()

class RasterSVGFromStream:

    def __init__(self, fin):
        self.fin = fin

    def process_frame(self, ctx, size, num):
        length = int(self.fin.readline().strip())
        svg_data = self.fin.read(length + 1)
        clock.tic('SVG read')
        svg_handle = rsvg.Handle(data=svg_data)
        clock.tic('SVG handle created')

        ctx.save()
        ctx.identity_matrix()
        svg_handle.render_cairo(ctx)
        ctx.restore()

def edit_frame(ctx, size, num):
    sheep_svg = rsvg.Handle("pecora.svg")

    ctx.scale (size[0]/4, size[1]/3)
    ctx.set_source_rgb(0.0, 1.0, 0.0)
    ctx.select_font_face("Ubuntu Medium",
                         cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(0.12)
    text = "MATEMATICI 1874 1110 FISICI"
    x_bearing, y_bearing, width, height = ctx.text_extents(text)[:4]
    # ctx.move_to(0.5 - width / 2 - x_bearing, 0.5 - height / 2 - y_bearing)
    ctx.move_to(0.1, 0.1 - y_bearing)
    ctx.show_text(text)

    ctx.identity_matrix()
    ctx.translate(2.0 * num, 350.0 + 50.0 * math.cos(2 * math.pi * num / 200.0))
    ctx.scale(0.25, 0.25)
    sheep_svg.render_cairo(ctx)

def main():
    num = 0
    fin = open('webpage_fifo')
    rsfs = RasterSVGFromStream(fin)
    try:
        while True:
            clock.tic('new cycle')
            image = read_frame(sys.stdin, pixel_format=TJPF_BGRX)
            clock.tic('frame read')
            #print >> sys.stderr, image.shape
            ctx, size, surf = get_cairo_context(image)
            clock.tic('cairo context created')
            #edit_frame(ctx, size, num)
            rsfs.process_frame(ctx, size, num)
            clock.tic('SVG rendered')
            surf.flush()
            clock.tic('surface flushed')
            write_frame(sys.stdout, image, pixel_format=TJPF_BGRX)
            clock.tic('frame written')
            clock.tic('cycle finished')
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
