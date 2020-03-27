from utils.configuration import Configuration
import time
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from kubernetes import client, config
from utils.wrappers import *
from utils.collectors import PredefinedVersionCollector
from utils.collectors import VersionCollector
from utils.versions import NodeVersion
from gcp.spanner import SpannerCollector
from party3rd.filebeat import FilebeatCollector
from party3rd.kubernetes_internal import K8Application
from party3rd.kubernetes_external import K8Releases
from azure.kubernetes import K8Azure
from gcp.kubernetes import K8GCP


def init(configuration: Configuration):
    name = configuration.name()
    applications = extract_applications()
    for application in applications.items():
        internal = PredefinedVersionCollector(application[1])
        external = FACTORY.instantiate_collector(application[0])
        REGISTRY.register(CommonWrapper(name, internal, external))

    # todo replace to api above!
    k8_internal = K8Application(configuration.kubernetes(), configuration.kubernetes_token())
    if configuration.is_aws():
        raise BaseException("AWS is not supported yet")
    elif configuration.is_gcp():
        k8_external = K8GCP(configuration)
        REGISTRY.register(KubernetesWrapper(name, k8_internal, k8_external))
    elif configuration.is_azure():
        k8_external = K8Azure(configuration)
        REGISTRY.register(KubernetesWrapper(name, k8_internal, k8_external))
    else:
        k8_external = K8Releases()
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
    return result


class CollectorFactory(object):
    value = {
        "spanner": SpannerCollector(),
        "filebeat": FilebeatCollector()
    }

    def instantiate_collector(self, application: str) -> VersionCollector:
        return self.value[application]


FACTORY = CollectorFactory()

if __name__ == '__main__':
    init(Configuration())
