import time
import prometheus_client
from utils.configuration import Configuration
from prometheus_client.core import REGISTRY
from kubernetes import config
from utils.producers import *


class ArmorMetricProducer(AbstractMetricProducer):
    k8: KubernetesMetricProducer
    ds: DaemonSetMetricProducer
    deploy: DeploymentMetricProducer
    sts: StatefulSetMetricProducer

    def __init__(self, installation: str, factory: CollectorFactory):
        super().__init__(installation)
        self.k8 = KubernetesMetricProducer(installation, factory)
        self.ds = DaemonSetMetricProducer(installation, factory)
        self.deploy = DeploymentMetricProducer(installation, factory)
        self.sts = StatefulSetMetricProducer(installation, factory)

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        return self.ds.collect() + self.deploy.collect() + self.sts.collect() + self.k8.collect()


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
    REGISTRY.register(ArmorMetricProducer(name, factory))

    port = configuration.port()
    logging.info(f"A.R.M.O.R is going to launch http server on {port}")
    prometheus_client.start_http_server(port)
    while True:
        time.sleep(1)
