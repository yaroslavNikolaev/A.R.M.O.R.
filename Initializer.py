import time
import typing
from configparser import ConfigParser
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server
from kubernetes import client, config
from wrappers import *
from utils.collectors import PredefinedVersionCollector
from utils.collectors import VersionCollector
from utils.versions import NodeVersion
from gcp.spanner import SpannerCollector
from party3rd.filebeat import FilebeatCollector


class Initializer(object):
    def __init__(self):
        pass

    def init(self, configuration: ConfigParser):
        name = configuration.get('common', 'name')
        applications = self.extract_applications()
        for application in applications.items():
            internal = PredefinedVersionCollector(application[1])
            external = FACTORY.instantiate_collector(application[0])
            REGISTRY.register(CommonWrapper.CommonWrapper(name, internal, external))

        start_http_server(configuration.getint('common', 'port', fallback=8080))
        if not configuration.get('common', 'kubernetes') or not configuration.get('common', 'kubernetes_token'):
            raise AssertionError("Kubernetes configuration has to be in place if you wish to use A.R.M.O.R.")
        REGISTRY.register(KubernetesWrapper.KubernetesWrapper(configuration))

        while True:
            time.sleep(1)

    def extract_applications(self) -> typing.Dict[str, NodeVersion]:
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
                    # todo consider case when version can be different for the same appication in different pods!
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
