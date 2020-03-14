import time
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from wrappers import *


class Initializer(object):
    def __init__(self):
        pass

    def init(self, args):
        start_http_server(args.port)
        # check for --version or -V
        if args.version:
            print("A.R.M.O.R. version is 0.0.2")

        REGISTRY.register(KubernetesWrapper.KubernetesWrapper(args))

        while True:
            time.sleep(1)
