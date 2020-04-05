import time
import prometheus_client
from utils.configuration import Configuration
from prometheus_client.core import REGISTRY
from kubernetes import config
from cachetools.func import ttl_cache
from utils.producers import *


class ArmorMetricProducer(AbstractMetricProducer):
    producers: typing.List[AbstractMetricProducer]
    state: typing.List[GaugeMetricFamily]

    def __init__(self, installation: str, factory: CollectorFactory):
        super().__init__(installation)
        self.state = []
        self.producers = []
        self.producers.append(DaemonSetMetricProducer(installation, factory))
        self.producers.append(DeploymentMetricProducer(installation, factory))
        self.producers.append(StatefulSetMetricProducer(installation, factory))
        self.producers.append(NamespaceMetricProducer(installation, factory))
        self.producers.append(NodeMetricProducer(installation, factory))
        self.producers.append(KubernetesMetricProducer(installation, factory))

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        return self.state

    # each 10 min
    @ttl_cache(maxsize=4, ttl=600)
    def prepare_metrics(self):
        result = []
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for producer in self.producers:
                futures.append(executor.submit(producer.collect))
            for future in futures:
                result += future.result()
        self.state = result


if __name__ == '__main__':
    '''
    Entry point of A.R.M.O.R. application. 
    Application expects several configuration files as input (config.ini and application.ini)
    '''
    logging.info("A.R.M.O.R is going to setup configuration")
    configuration = Configuration()
    factory = CollectorFactory(configuration)
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config(configuration.kubernetes_config())

    logging.info("A.R.M.O.R is going to create metric producers.")
    name = configuration.name()
    REGISTRY.register(SeverityFactorProducer(name))
    armor = ArmorMetricProducer(name, factory)
    armor.prepare_metrics()
    REGISTRY.register(armor)

    port = configuration.port()
    logging.info(f"A.R.M.O.R is going to launch http server on {port}")
    prometheus_client.start_http_server(port)
    while True:
        armor.prepare_metrics()
        time.sleep(1)
