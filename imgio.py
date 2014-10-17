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
    return cv2.imencode("image.jpeg", image)[1].data

# The PyTJ interface is terrible, but it is the best I could come up
# with, considered that I don't want to spend on it more time then
# strictly necessary; please, don't reuse it on serious things

import pytj
from pytj import TJPF_RGBX, TJPF_BGRX
tj_ctx = pytj.create_tjcontext()

def tj_open_from_data(data, pixel_format=TJPF_RGBX):
    res = pytj.decode_image(tj_ctx, data, len(data), pixel_format, pytj.TJFLAG_FASTDCT)
    as_str = pytj.cdata(res.buf, res.width * res.height * 4)
    pytj.free_decoded_image(res.buf)
    image = numpy.ndarray(shape=(res.height, res.width, 4), dtype='uint8', buffer=as_str)
    image = numpy.copy(image)
    #print >> sys.stderr, image.__array_interface__

    return image

def tj_write_to_data(image, pixel_format=TJPF_RGBX):
    height, width, channels = image.shape
    #print >> sys.stderr, image.__array_interface__
    res = pytj.encode_image(tj_ctx, image.__array_interface__['data'][0], width, height, pixel_format, pytj.TJSAMP_444, 75, pytj.TJFLAG_FASTDCT)
    as_str = pytj.cdata(res.buf, res.len)
    pytj.free_encoded_image(res.buf)

    return as_str

#jpeg_interface = [pil_open_from_data, pil_write_to_data]
#jpeg_interface = [cv2_open_from_data, cv2_write_to_data]
jpeg_interface = [tj_open_from_data, tj_write_to_data]

def read_frame(fin, **kwargs):
    length_tag = fin.read(4)
    length, = struct.unpack("!I", length_tag)
    imdata = fin.read(length)
    image = jpeg_interface[0](imdata, **kwargs)

    return image

def write_frame(fout, image, **kwargs):
    imdata = jpeg_interface[1](image, **kwargs)
    length = len(imdata)
    length_tag = struct.pack("!I", length)
    fout.write(length_tag)
    fout.write(imdata)

# Read a RAW frame, which is assumed to be RGBA and of known size
def read_raw_frame(fin, width, height):
    length = width * height * 4
    imdata = fin.read(length)
    image = numpy.ndarray(shape=(height, width, 4), dtype='uint8', buffer=imdata)
    image = numpy.copy(image)
    return image

def get_cairo_image(image):
    height, width, channels = image.shape
    size = (width, height)
    assert channels == 4
    surf = cairo.ImageSurface.create_for_data(image.data, cairo.FORMAT_ARGB32, width, height)

    return size, surf

def swap_channels(image):
    """Swap R and B channels.

    """
    return numpy.dstack([image[:,:,2], image[:,:,1], image[:,:,1], image[:,:,3]])

def get_cairo_context(image):
    height, width, channels = image.shape
    size = (width, height)
    assert channels == 4
    surf = cairo.ImageSurface.create_for_data(image.data, cairo.FORMAT_RGB24, width, height)
    ctx = cairo.Context(surf)

    # Set up a reasonable coordinate system
    #versor_len = 0.7 * min(size)
    #reflect = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
    #ctx.transform(reflect)
    #ctx.translate(size[0]/2, -size[1]/2)
    #ctx.scale(versor_len, versor_len)

    # Setup reasonable drawing tools
    #ctx.set_line_width(1.5 / versor_len)
    #ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    #ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    return ctx, size, surf
