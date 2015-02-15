#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from imgio import read_jpeg_frame, write_jpeg_frame


def main():
    delay = float(sys.argv[1])

    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            write_jpeg_frame(sys.stdout, imdata, timestamp + delay)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
