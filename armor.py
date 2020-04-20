import kubernetes.config, shutil
from utils.configuration import Configuration
from utils.producers import *
from storages import prometheus

K8_CONFIG_LOCATION = "./k8config"


def load_k8_config(cfg: Configuration):
    if cfg.internal():
        kubernetes.config.load_incluster_config()
    else:
        external_k8_config = cfg.config()
        # in case of secret mount, we should be able to update file
        shutil.copy(external_k8_config, K8_CONFIG_LOCATION)
        kubernetes.config.load_kube_config(config_file=K8_CONFIG_LOCATION)


if __name__ == '__main__':
    '''
    Entry point of A.R.M.O.R. application. 
    Application expects configuration file as input [application.yaml]. 
    Name and file location can be overwritten via cli , check --help
    '''
    try:
        logging.info("A.R.M.O.R is going to setup configuration")
        configuration = Configuration()
        load_k8_config(configuration)
        # move to factory as soon as new type of storage will be introduced (add to auto doc as well)
        storage = prometheus.PrometheusStorage(configuration)
        factory = CollectorFactory(configuration)
        cluster = configuration.name()
        logging.info("A.R.M.O.R is going to create and register metric producers.")
        # move to scanners as well (add auto doc as well)
        storage.register(DaemonSetMetricProducer(cluster, factory))
        storage.register(DeploymentMetricProducer(cluster, factory))
        storage.register(StatefulSetMetricProducer(cluster, factory))
        storage.register(NamespaceMetricProducer(cluster, factory))
        storage.register(NodeMetricProducer(cluster, factory))
        storage.register(KubernetesMetricProducer(cluster, factory, configuration.cloud()))
    except Exception as e:
        logging.warning(f'Error startup', exc_info=True)
        raise e
