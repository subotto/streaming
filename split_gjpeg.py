#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import datetime
import struct

from imgio import read_jpeg_frame, write_jpeg_frame, read_jpeg_header

STRUCT = struct.Struct("!IdQ")
STRUCT_SIZE = STRUCT.size

def main():
    file_size = int(sys.argv[1])
    print >> sys.stderr, "Splitting in pieces not larger than %d bytes..." % (file_size)
    last_begin = 0
    last_pos = 0
    while True:
        block = sys.stdin.read(STRUCT_SIZE)
        if block == '':
            break
        frame_num, timestamp, pos = STRUCT.unpack(block)
        if pos - last_begin <= file_size:
            last_pos = pos
        else:
            print "%d" % (last_pos)
            last_begin = last_pos

if __name__ == '__main__':
    main()
