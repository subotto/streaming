#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys

from imgio import read_jpeg_frame, write_jpeg_frame


def main():
    num = 0
    last_timestamp = None
    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            now = time.time()
            if last_timestamp is not None:
                diff = now - last_timestamp
                print >> sys.stderr, "> FPS: %f, delay: %f" % (1.0 / diff, now - timestamp)
            last_timestamp = now
            write_jpeg_frame(sys.stdout, imdata, timestamp)
            num += 1
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
