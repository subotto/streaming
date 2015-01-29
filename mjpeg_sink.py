#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct

from imgio import read_jpeg_frame

def main():
    num = 0
    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            if imdata == '':
                break
            sys.stdout.write(imdata)
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
