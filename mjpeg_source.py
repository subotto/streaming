#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct

from imgio import write_jpeg_frame, read_unbounded_jpeg_frame

SOI_TAG = '\xff\xd8'
EOI_TAG = '\xff\xd9'
SOS_TAG = '\xff\xda'
TAG_WITHOUT_LENGTH = ['\xff\xd8',
                      '\xff\x01',
                      '\xff\xd0',
                      '\xff\xd1',
                      '\xff\xd2',
                      '\xff\xd3',
                      '\xff\xd4',
                      '\xff\xd5',
                      '\xff\xd6',
                      '\xff\xd7',
                      '\xff\xd9',
                  ]

def main():
    num = 0
    try:
        while True:
            content = read_unbounded_jpeg_frame(sys.stdin)
            if content is None:
                break
            write_jpeg_frame(sys.stdout, content)
            print >> sys.stderr, num
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
