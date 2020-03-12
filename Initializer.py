import time
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from party3rd import *
import aws
import azure
import gcp
import party3rd


class Initializer(object):
    def __init__(self):
        pass

    def init(self, args):
        start_http_server(8000)
        # check for --version or -V
        if args.version:
            print("A.R.M.O.R. version is 0.1")
        if args.kubernetes and args.kubernetes_token:
            REGISTRY.register(kubernetes.K8(args.kubernetes, args.kubernetes_token))

        while True:
            time.sleep(1)
