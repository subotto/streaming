#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import struct

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

# See https://stackoverflow.com/questions/1557071/the-size-of-a-jpegjfif-image for information
def read_jpeg(fin):
    data = []

    # Read the SOI tag (or check that the stream was finished)
    tag = fin.read(2)
    data.append(tag)
    if tag == '':
        return
    assert tag == SOI_TAG

    read_tag = None

    while True:
        # Read the tag
        if read_tag is None:
            tag = fin.read(2)
            data.append(tag)
        else:
            tag = read_tag
        #print >> sys.stderr, repr(tag)
        assert len(tag) == 2
        assert tag[0] == '\xff'

        # If we have EOI, we're done!
        if tag == EOI_TAG:
            break

        # Some tag have no payload, skip them
        if tag in TAG_WITHOUT_LENGTH:
            continue

        # Read payload length
        length_bytes = fin.read(2)
        assert len(length_bytes) == 2
        data.append(length_bytes)
        length, = struct.unpack("!H", length_bytes)
        #print >> sys.stderr, length

        # Read payload
        payload = fin.read(length - 2)
        assert len(payload) == length - 2
        data.append(payload)

        # SOS packets have additional data after the payload; it's ok
        # to search for a new marker, because markers cannot occur in
        # such data
        read_tag = None
        if tag == SOS_TAG:
            prev_ff = False
            while True:
                byte = fin.read(1)
                data.append(byte)
                #print >> sys.stderr, repr(byte),
                if prev_ff and byte != '\x00':
                    read_tag = '\xff' + byte
                    break
                prev_ff = (byte == '\xff')

    return "".join(data)

def main():
    num = 0
    try:
        while True:
            content = read_jpeg(sys.stdin)
            if content is None:
                break
            content = struct.pack("!I", len(content)) + content
            sys.stdout.write(content)
            print >> sys.stderr, num
            num += 1
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
