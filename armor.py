import time
import logging
from factory import CollectorFactory
from utils.configuration import Configuration
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from kubernetes import client, config
from utils.wrappers import *
from utils.versions import NodeVersion


def init(collectors_factory: CollectorFactory, configuration: Configuration):
    name = configuration.name()
    applications = extract_applications()
    for application in applications.items():
        internal = collectors_factory.get_predefined_collector(application[1])
        external = collectors_factory.instantiate_collector(application[0])
        REGISTRY.register(CommonWrapper(name, internal, external))

    # todo replace to api above!
    k8_internal = collectors_factory.instantiate_collector("K8Application")
    k8_external = collectors_factory.instantiate_collector(configuration.kubernetes_application())
    REGISTRY.register(KubernetesWrapper(name, k8_internal, k8_external))

    start_http_server(configuration.port())
    while True:
        time.sleep(1)


def extract_applications() -> typing.Dict[str, NodeVersion]:
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
    result = dict()
    for i in ret.items:
        if i.metadata.annotations is None:
            continue
        for annotation in i.metadata.annotations.keys():
            if "armor.io" in annotation:
                application = annotation.split("/")[1]
                version = i.metadata.annotations[annotation]
                # todo consider case when version can be different for the same tooling in different pods!
                result[application] = NodeVersion(version, i.metadata.name)
                logging.info(f'New application {i.metadata.name} with version {version}')
    return result


if __name__ == '__main__':
    cfg = Configuration()
    factory = CollectorFactory(cfg)
    init(factory, cfg)
