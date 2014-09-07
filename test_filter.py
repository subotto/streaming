#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo
import rsvg
import math

from imgio import read_frame, write_frame, get_cairo_context

sheep_svg = rsvg.Handle("pecora.svg")

def edit_frame(ctx, size, num):
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
