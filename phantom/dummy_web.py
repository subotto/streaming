#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import sys
import json
import os

MAX_QUERY_STRING_LEN = 1024

class Application:

    def __init__(self):
        self.start_time = time.time()
        self.encoder = json.JSONEncoder(indent=2)
        self.events = []

    def error(self, environ, start_response):
        status = '400 Bad Request'
        response = '400 Bad Request'
        response_headers = [('Content-Type', 'text/plain; charset=utf-8'),
                            ('Content-Length', str(len(response)))]
        start_response(status, response_headers)
        return [response]

    def __call__(self, environ, start_response):
        # Parse the request
        if 'QUERY_STRING' in environ and environ['QUERY_STRING'] is not None:
            query_string = environ['QUERY_STRING']
            if len(query_string) >= MAX_QUERY_STRING_LEN:
                return self.error(environ, start_response)
            try:
                request_tuples = [tuple(x.split('=', 1)) for x in environ['QUERY_STRING'].split('&')]
                request_params = dict([x for x in request_tuples if len(x) == 2])
                last_event = int(request_params.get('last_event', 1))
            except Exception:
                #raise
                return self.error(environ, start_response)

        obj_response = {
            'red_score': None,
            'blue_score': None,
            'red_team': None,
            'blue_team': None,
            'events': None,
            'version': 1,
            }
        json_response = self.encoder.encode(obj_response).encode('utf-8')
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json; charset=utf-8'),
                            ('Content-Length', str(len(json_response)))]
        start_response(status, response_headers)
        return [json_response]

if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        application = Application()
        httpd = make_server('', 8000, application)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

else:
    application = Application()
