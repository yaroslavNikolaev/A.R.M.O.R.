import time
import prometheus_client
from utils.configuration import Configuration
from prometheus_client.core import REGISTRY
from kubernetes import config
from utils.metric_producers import *

if __name__ == '__main__':
    logging.info("A.R.M.O.R is going to setup configuration")
    configuration = Configuration()
    factory = CollectorFactory(configuration)
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    logging.info("A.R.M.O.R is going to create metric producers.")
    name = configuration.name()
    REGISTRY.register(ApplicationMetricProducer(name, factory))
    REGISTRY.register(KubernetesMetricProducer(name, factory))

    port = configuration.port()
    logging.info(f"A.R.M.O.R is going to launch http server on {port}")
    prometheus_client.start_http_server(port)
    while True:
        time.sleep(1)
