#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import datetime

from imgio import read_jpeg_frame, write_jpeg_frame

def main():
    epoch = datetime.datetime(1970, 1, 1)
    begin = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d %H:%M:%S')
    begin_ts = (begin - epoch).total_seconds()
    end_ts = (begin - epoch).total_seconds()

    frame_num = 0
    while True:
        if frame_num % 1000 == 0:
            print >> sys.stderr, "\rProcessed %d frames" % (frame_num)
        imdata, timestamp = read_jpeg_frame(sys.stdin)
        if imdata is None:
            break
        if begin_ts <= timestamp <= end_ts:
            write_jpeg_frame(sys.stdout, imdata, timestamp)
        if timestamp > end_ts:
            break
        frame_num += 1

if __name__ == '__main__':
    main()
