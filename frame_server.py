#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import StringIO

from net import ImageSocketServer
from imgio import read_jpeg_frame, write_jpeg_frame


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    server = ImageSocketServer(host, port)

    num = 0
    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            tmp = StringIO.StringIO()
            write_jpeg_frame(tmp, imdata, timestamp)
            server.post_data(tmp.getvalue())
            num += 1
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
