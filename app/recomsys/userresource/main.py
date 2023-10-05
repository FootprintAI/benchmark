#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from prometheus_client import start_http_server, Summary, Histogram
from urllib.parse import parse_qs
import logging
import numpy as np
import os
import time


REQUEST_TIME = Summary('get_userinfo_request_processing_seconds', 'Time spent processing request')
REQUEST_HIST = Histogram('get_userinfo_request_processing_seconds_hist', 'Description of histogram')

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def get_delay_dist(self):
        mu = float(os.environ.get("USER_DELAY_MU", "0"))
        sigma = float(os.environ.get("USER_DELAY_SIGMA", "0.1"))
        return mu, sigma

    @REQUEST_TIME.time()
    @REQUEST_HIST.time()
    def do_GET(self):
        #logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        mu, sigma = self.get_delay_dist()
        s = np.random.normal(mu, sigma, 1)
        delayInS = abs(s[0])
        pathparam = parse_qs(self.path.partition('?')[-1])
        logging.info("userid:{}, delay:{}, mu:{}, sigma:{}".format(pathparam['userid'], delayInS, mu, sigma))
        time.sleep(delayInS) # to millisecond
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run(server_class=ThreadedHTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    # start metrics service
    start_http_server(50999)

    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
