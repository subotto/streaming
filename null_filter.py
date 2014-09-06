#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo

from imgio import read_frame, write_frame, get_cairo_context

def edit_frame(ctx, size):
    pass

def main():
    try:
        while True:
            image = read_frame(sys.stdin)
            #print >> sys.stderr, image.shape
            ctx, size = get_cairo_context(image)
            edit_frame(ctx, size)
            write_frame(sys.stdout, image)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
