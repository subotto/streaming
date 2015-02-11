#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys

from net import ImageMultiClient

def main():
    servers = [(("localhost", 2204), 10.0),
               (("localhost", 2205), 10.0)]
    client = ImageMultiClient(servers)
    while True:
        client.write_status()
        time.sleep(0.3)
        while True:
            #print "advance"
            res = client.advance_to_stream(0)
            if not res:
                break

if __name__ == '__main__':
    main()
