#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import datetime
import struct

from imgio import read_jpeg_frame, write_jpeg_frame, read_jpeg_header

def main():
    frame_num = 0
    while True:
        if frame_num % 1000 == 0:
            print >> sys.stderr, "\rProcessed %d frames" % (frame_num)
        pos = sys.stdin.tell()
        length, timestamp = read_jpeg_header(sys.stdin)
        if length is None:
            break
        sys.stdout.write(struct.pack("!IdQ", frame_num, timestamp, pos))
        frame_num += 1

    print >> sys.stderr, "\rProcessed %d frames" % (frame_num)

if __name__ == '__main__':
    main()
