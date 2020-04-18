from utils.configuration import Configuration
from utils.producers import *
from storages import prometheus

if __name__ == '__main__':
    '''
    Entry point of A.R.M.O.R. application. 
    Application expects several configuration files as input (config.ini and application.ini)
    '''
    try:
        logging.info("A.R.M.O.R is going to setup configuration")
        configuration = Configuration()
        factory = CollectorFactory(configuration)
        # move to factory as soon as new type of storage will be introduced (add to auto doc as well)
        storage = prometheus.PrometheusStorage(configuration)
        logging.info("A.R.M.O.R is going to create and register metric producers.")
        cluster = configuration.name()
        # move to scanners as well (add auto doc as well)
        storage.register(DaemonSetMetricProducer(cluster, factory))
        storage.register(DeploymentMetricProducer(cluster, factory))
        storage.register(StatefulSetMetricProducer(cluster, factory))
        storage.register(NamespaceMetricProducer(cluster, factory))
        storage.register(NodeMetricProducer(cluster, factory))
        storage.register(KubernetesMetricProducer(cluster, factory))
    except Exception as e:
        logging.warning(f'Error startup', exc_info=True)
        raise e
