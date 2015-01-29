#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct

from imgio import read_jpeg_frame

def main():
    num = 0
    ext = sys.argv[1]
    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            with open("frames/frame_%06d.%s" % (num, ext), 'w') as fout:
                fout.write(imdata)
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
