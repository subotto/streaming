#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time

from imgio import write_jpeg_frame

def main():
    filename = sys.argv[1]
    fps = 0.0
    if len(sys.argv) > 2:
        fps = float(sys.argv[2])

    with open(filename) as fin:
        content = fin.read()

    num = 0
    try:
        while True:
            write_jpeg_frame(sys.stdout, content, time.time())
            #print >> sys.stderr, num
            num += 1
            if fps != 0.0:
                time.sleep(1.0 / fps)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
