#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import StringIO

from imgio import write_jpeg_frame, read_jpeg_frame
from net import WritingThread

def main():
    filename = sys.argv[1]
    fps = 0.0
    if len(sys.argv) > 2:
        fps = float(sys.argv[2])

    #with open(filename) as fin:
    #    content = fin.read()
    fin = open(filename)

    num = 0
    if fps > 0.0:
        fout = WritingThread(sys.stdout)
    else:
        fout = sys.stdout
    try:
        while True:
            before = time.time()
            #timestamp = time.time()
            content, timestamp = read_jpeg_frame(fin)
            write_jpeg_frame(fout, content, timestamp)
            #print >> sys.stderr, num
            num += 1
            if fps != 0.0:
                after = time.time()
                delay = 1.0 / fps - (after - before)
                if delay > 0.0:
                    time.sleep(delay)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
