#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import sys
import json
import os
import math
import random

MAX_QUERY_STRING_LEN = 1024

class Application:

    def __init__(self):
        self.start_time = time.time()
        self.encoder = json.JSONEncoder(indent=2)
        self.events = []
        self.event_num = 0
        self.swapped = True
        self.swap_k = -1

    def error(self, environ, start_response):
        status = '400 Bad Request'
        response = '400 Bad Request'
        response_headers = [('Content-Type', 'text/plain; charset=utf-8'),
                            ('Content-Length', str(len(response)))]
        start_response(status, response_headers)
        return [response]

    def generate_events(self, now):
        # Generate swap event every 10*e seconds
        swap_off = int((now - self.start_time) / (10 * math.e))
        if swap_off > self.swap_k:
            self.swap_k = swap_off
            self.events.append((self.event_num, {"type": "swap"}))
            self.event_num += 1
            self.swapped = not self.swapped

        # Randomly generate change events
        if random.uniform(0.0, 1.0) > 0.9:
            team = random.choice(["red", "blue"])
            self.events.append((self.event_num, {"type": "change",
                                                 "team": team,
                                                 "player_a": "Duffy Duck",
                                                 "player_b": "Mickey Mouse"}))
            self.event_num += 1

    def __call__(self, environ, start_response):
        # Parse the request
        if 'QUERY_STRING' in environ and environ['QUERY_STRING'] is not None:
            query_string = environ['QUERY_STRING']
            if len(query_string) >= MAX_QUERY_STRING_LEN:
                return self.error(environ, start_response)
            try:
                request_tuples = [tuple(x.split('=', 1)) for x in environ['QUERY_STRING'].split('&')]
                request_params = dict([x for x in request_tuples if len(x) == 2])
                last_event = int(request_params.get('last_event', -1))
            except Exception:
                #raise
                return self.error(environ, start_response)

        # Delete expired events
        self.events = [(num, ev) for (num, ev) in self.events if num > last_event]

        # Create dummy data
        now = time.time()
        self.generate_events(now)
        math_score = int((now - self.start_time) / 5)
        phys_score = int((now - self.start_time) / (5 * math.pi / 2.0))
        if not self.swapped:
            red_score = math_score
            blue_score = phys_score
            red_team = "Matematici"
            blue_team = "Fisici"
        else:
            red_score = phys_score
            blue_score = math_score
            red_team = "Fisici"
            blue_team = "Matematici"

        # Send response
        obj_response = {
            'red_score': red_score,
            'blue_score': blue_score,
            'red_team': red_team,
            'blue_team': blue_team,
            'events': self.events,
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
