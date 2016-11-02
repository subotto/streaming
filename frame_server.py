#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import StringIO
import time

from net import ImageSocketServer
from imgio import read_jpeg_frame, write_jpeg_frame


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    server = ImageSocketServer(host, port)

    num = 0
    time_offset = None
    limiter = True
    try:
        while True:
            imdata, timestamp = read_jpeg_frame(sys.stdin)
            if limiter:
                now = time.time()
                if time_offset is None:
                    time_offset = now - timestamp
                else:
                    sleep_time = time_offset + timestamp - now
                    if sleep_time > 0:
                        time.sleep(sleep_time)
            tmp = StringIO.StringIO()
            write_jpeg_frame(tmp, imdata, timestamp)
            server.post_data(tmp.getvalue())
            num += 1
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
