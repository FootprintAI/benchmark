#!/usr/bin/env python3
"""
License: MIT License
Copyright (c) 2023 Miel Donkers
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import start_http_server, Summary, Histogram
from urllib.parse import parse_qs
import json
import logging
import requests
import time
import urllib.parse

from inference import find_similar_movies
from scipy import sparse
from scipy.sparse import csr_matrix
from urllib.parse import parse_qs

userprofile_url = "http://recomsys-userresource-service.recomsys.svc.cluster.local"
X = sparse.load_npz("rating-matrix.npz")

REQUEST_TIME = Summary('post_inference_request_processing_seconds', 'Time spent processing request')
REQUEST_HIST = Histogram('post_inference_request_processing_seconds_hist', 'Description of histogram')

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    @REQUEST_TIME.time()
    @REQUEST_HIST.time()
    def do_POST(self):
        start_time = time.time()

        pathparam = parse_qs(self.path.partition('?')[-1])
        logging.info(pathparam)
        userid = pathparam['userid'][0] if 'userid' in pathparam else ""
        # fetch user profile
        path_params = {
            'userid': userid,
        }
        prefetch_url = "{}?{}".format(userprofile_url, urllib.parse.urlencode(path_params))
        logging.info("prefetch url: {}".format(prefetch_url))
        requests.get(prefetch_url)

        # prepare the payload for inference
        found = find_similar_movies(3, self.X, k=10)
        logging.info("recomsys:{}".format(found))

        self._set_response()
        self.wfile.write("POST request for {} cost {}".format(self.path, time.time() - start_time).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
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
    start_http_server(50999)

    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
