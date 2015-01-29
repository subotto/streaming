#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct
import time

from imgio import write_jpeg_frame, read_unbounded_jpeg_frame

def main():
    num = 0
    try:
        while True:
            content = read_unbounded_jpeg_frame(sys.stdin)
            if content is None:
                break
            write_jpeg_frame(sys.stdout, content, time.time())
            print >> sys.stderr, num
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
