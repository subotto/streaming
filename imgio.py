#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import StringIO
import cairo

import PIL.Image

def pil_open_from_data(data):
    return PIL.Image.open(StringIO.StringIO(data))

def pil_write_to_data(image):
    fout = StringIO.StringIO()
    image.save(fout, "jpeg")
    return fout.getvalue()

# It doesn't work...
#import jpeg

def jpeg_open_from_data(data):
    return jpeg.decompress(data)

def jpeg_write_to_data(image):
    return jpeg.compress(*image)

import numpy
import cv
import cv2

def cv2_open_from_data(data):
    return cv2.imdecode(numpy.frombuffer(data, dtype='uint8'), -1)

def cv2_write_to_data(image):
    #params = [cv.CV_IMWRITE_JPEG_QUALITY, 50, cv.CV_IMWRITE_PNG_COMPRESSION, 0]
    return cv2.imencode("image.png", image)[1].data

#jpeg_interface = [pil_open_from_data, pil_write_to_data]
jpeg_interface = [cv2_open_from_data, cv2_write_to_data]

def read_frame(fin):
    length_tag = fin.read(4)
    length, = struct.unpack("!I", length_tag)
    imdata = fin.read(length)
    image = jpeg_interface[0](imdata)

    return image

def write_frame(fout, image):
    imdata = jpeg_interface[1](image)
    length = len(imdata)
    length_tag = struct.pack("!I", length)
    fout.write(length_tag)
    fout.write(imdata)

def get_cairo_context(image):
    width, height, channels = image.shape
    assert channels == 4
    surf = cairo.ImageSurface.create_for_data(image.data, cairo.FORMAT_RGB24, width, height)
    ctx = cairo.Context(surf)

    # Set up a reasonable coordinate system
    size = (width, height)
    versor_len = 0.7 * min(size)
    reflect = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
    ctx.transform(reflect)
    ctx.translate(size[0]/2, -size[1]/2)
    ctx.scale(versor_len, versor_len)

    ctx.set_line_width(1.5 / versor_len)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    return ctx, size
