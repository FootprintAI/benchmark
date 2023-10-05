#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from prometheus_client import start_http_server, Summary, Histogram
from urllib.parse import parse_qs
import os
import json
import logging
import numpy as np
import pickle
import requests
import time
import urllib.parse

from concurrent.futures import ThreadPoolExecutor # pip install futures
from inference import find_similar_movies
from scipy import sparse
from scipy.sparse import csr_matrix
from urllib.parse import parse_qs

userprofile_url = "http://recomsys-userresource-service.bench.svc.cluster.local"

m = pickle.load(open('movielens20m.model.pkl', "rb"))
X = m["model"]
dims = m["dims"]

REQUEST_TIME = Summary('post_inference_request_processing_seconds', 'Time spent processing request')
REQUEST_HIST = Histogram('post_inference_request_processing_seconds_hist', 'Description of histogram')

def random_item_feature(dims: int):
    import random
    features = []
    for i in range (dims):
        features.append(random.randint(0,5))
    return np.array(features)


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    @REQUEST_TIME.time()
    @REQUEST_HIST.time()
    def do_POST(self):
        global dims
        global X 

        start_time = time.time()

        pathparam = parse_qs(self.path.partition('?')[-1])
        userid = pathparam['userid'][0] if 'userid' in pathparam else ""
        # fetch user profile
        path_params = {
            'userid': userid,
        }
        prefetch_url = "{}?{}".format(userprofile_url, urllib.parse.urlencode(path_params))
        logging.info("prefetch url: {}".format(prefetch_url))
        time1 = time.time()
        requests.get(prefetch_url)
        delta1 = time.time() - time1

        # prepare the payload for inference
        time2 = time.time()
        found = find_similar_movies(random_item_feature(dims), X)
        delta2 = time.time() - time2
        delta3 = time.time() - start_time

        logging.info("time delata: d1:{}, d2:{}, d3:{}, total:{}".format(delta1, delta2, delta3, time.time() - start_time))
        self._set_response()
        self.wfile.write("served at {}, POST request for {} cost {} / {}".format(__file__, self.path, delta1, delta2).encode('utf-8'))

class PoolMixIn(ThreadingMixIn):
    def process_request(self, request, client_address):
        self.pool.submit(self.process_request_thread, request, client_address)

class PoolHTTPServer(PoolMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    thread_pool_size = os.environ.get("HTTP_THREAD_POOL_SIZE", "2")
    pool = ThreadPoolExecutor(max_workers=int(thread_pool_size))


def run(server_class=PoolHTTPServer, handler_class=S, port=8080):
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
