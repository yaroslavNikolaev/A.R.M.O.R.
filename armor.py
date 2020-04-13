import time
import prometheus_client
from utils.configuration import Configuration
from prometheus_client.core import REGISTRY
from cachetools.func import ttl_cache
from utils.producers import *


class ArmorMetricProducer(AbstractMetricProducer):
    producers: typing.List[AbstractMetricProducer]
    state: typing.List[GaugeMetricFamily]

    def __init__(self, cluster: str, factory: CollectorFactory):
        super().__init__(cluster)
        self.state = []
        self.producers = []
        self.producers.append(DaemonSetMetricProducer(cluster, factory))
        self.producers.append(DeploymentMetricProducer(cluster, factory))
        self.producers.append(StatefulSetMetricProducer(cluster, factory))
        self.producers.append(NamespaceMetricProducer(cluster, factory))
        self.producers.append(NodeMetricProducer(cluster, factory))
        self.producers.append(KubernetesMetricProducer(cluster, factory))

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        return self.state

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
    try:
        logging.info("A.R.M.O.R is going to setup configuration")
        configuration = Configuration()
        factory = CollectorFactory(configuration)

        logging.info("A.R.M.O.R is going to create metric producers.")
        cluster = configuration.name()
        REGISTRY.register(SeverityFactorProducer(cluster))
        armor = ArmorMetricProducer(cluster, factory)
        armor.prepare_metrics()
        REGISTRY.register(armor)
        port = configuration.port()
        logging.info(f"A.R.M.O.R is going to launch http server on {port}")
        prometheus_client.start_http_server(port)
        while True:
            armor.prepare_metrics()
            time.sleep(1)

    except Exception as e:
        logging.warning(f'Error startup', exc_info=True)
        raise e
