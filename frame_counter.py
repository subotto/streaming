#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from imgio import read_jpeg_frame, write_jpeg_frame


def main():
    num = 0
    last_timestamp = None
    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            if last_timestamp is not None:
                diff = timestamp - last_timestamp
                print >> sys.stderr, "> FPS: %f" % (1.0 / diff)
            last_timestamp = timestamp
            write_jpeg_frame(sys.stdout, imdata, timestamp)
            num += 1
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
