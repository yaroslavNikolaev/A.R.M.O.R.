import time
from configparser import ConfigParser
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from wrappers import *


class Initializer(object):
    def __init__(self):
        pass

    def init(self, config: ConfigParser):
        start_http_server(config.getint('common', 'port', fallback=8080))
        if not config.get('common', 'kubernetes') or not config.get('common', 'kubernetes_token'):
            raise AssertionError("Kubernetes configuration has to be in place if you wish to use A.R.M.O.R.")
        REGISTRY.register(KubernetesWrapper.KubernetesWrapper(config))

        while True:
            time.sleep(1)
