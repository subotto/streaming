#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import StringIO

from imgio import write_jpeg_frame
from net import WritingThread

def main():
    filename = sys.argv[1]
    fps = 0.0
    if len(sys.argv) > 2:
        fps = float(sys.argv[2])

    with open(filename) as fin:
        content = fin.read()

    num = 0
    last_write = None
    fout = WritingThread(sys.stdout)
    try:
        while True:
            write_jpeg_frame(fout, content, time.time())
            #print >> sys.stderr, num
            num += 1
            if fps != 0.0:
                now = time.time()
                if last_write is not None:
                    delay = 1.0 / fps - (now - last_write)
                    if delay > 0.0:
                        time.sleep(delay)
                last_write = now
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
