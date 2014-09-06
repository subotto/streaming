#!/usr/bin/env python

import math
import cairo
import rsvg

WIDTH, HEIGHT = 640, 480

surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context (surface)

ctx.scale (WIDTH/4, HEIGHT/3) # Normalizing the canvas

"""
pat = cairo.LinearGradient (0.0, 0.0, 0.0, 1.0)
pat.add_color_stop_rgba (1, 0.7, 0, 0, 0.5) # First stop, 50% opacity
pat.add_color_stop_rgba (0, 0.9, 0.7, 0.2, 1) # Last stop, 100% opacity

ctx.rectangle (0, 0, 4, 3) # Rectangle(x0, y0, x1, y1)
ctx.set_source (pat)
ctx.fill ()

ctx.translate (0.1, 0.1) # Changing the current transformation matrix

ctx.move_to (0, 0)
ctx.arc (0.2, 0.1, 0.1, -math.pi/2, 0) # Arc(cx, cy, radius, start_angle, stop_angle)
ctx.line_to (0.5, 0.1) # Line to (x,y)
ctx.curve_to (0.5, 0.2, 0.5, 0.4, 0.2, 0.8) # Curve(x1, y1, x2, y2, x3, y3)
ctx.close_path ()

ctx.set_source_rgb (0.3, 0.2, 0.5) # Solid color
ctx.set_line_width (0.02)
ctx.stroke ()
"""


# Scrivere un testo
ctx.set_source_rgb(0.0, 0.0, 0.0)
ctx.select_font_face("Ubuntu Medium",
        cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
ctx.set_font_size(0.12)
text = "MATEMATICI 1874 1110 FISICI"
x_bearing, y_bearing, width, height = ctx.text_extents(text)[:4]
# ctx.move_to(0.5 - width / 2 - x_bearing, 0.5 - height / 2 - y_bearing)
ctx.move_to(0.1, 0.1 - y_bearing)
ctx.show_text(text)

ctx.move_to(0,0);
# Caricare SVG
h = rsvg.Handle("immagine2.svg")
#s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100) 
#ctx = cairo.Context(s)
#h.render_cairo(ctx)



surface.write_to_png ("example.png") # Output to PNG

