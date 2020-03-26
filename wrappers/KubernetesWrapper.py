import typing
from configparser import ConfigParser
from .CommonWrapper import CommonWrapper
from .CommonWrapper import EMPTY_ARRAY
from prometheus_client.core import GaugeMetricFamily
from party3rd.kubernetes_internal import K8Application
from party3rd.kubernetes_external import K8Releases
from azure.kubernetes import K8Azure
from gcp.kubernetes import K8GCP
from utils.versions import NodeVersion


class KubernetesWrapper(CommonWrapper):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    BARE_METAL = "metal"

    def __init__(self, args: ConfigParser):
        k8_external = None
        if args.has_section(self.AWS):
            raise BaseException("AWS is not supported yet")
        elif args.has_section(self.GCP):
            k8_external = K8GCP(args[self.GCP])
        elif args.has_section(self.AZURE):
            k8_external = K8Azure(args[self.AZURE])
        elif args.has_section(self.BARE_METAL):
            k8_external = K8Releases()
        if not k8_external:
            return
        k8_internal = K8Application(args.get('common', 'kubernetes'), args.get('common', 'kubernetes_token'))
        super().__init__(args.get('common', 'name', fallback='armor'), k8_internal, k8_external)

    def collect(self) -> typing.List[GaugeMetricFamily]:
        if not self.active:
            return EMPTY_ARRAY
        external_versions = self.external_collector.collect()
        internal_versions = self.internal_collector.collect()
        result = []
        for internal_version in internal_versions:
            is_master = internal_version.node_name == "master"
            filter_function = self.__filter_master_version if is_master else self.__filter_node_versions
            result += super().extract_metrics(internal_version, filter(filter_function, external_versions))
        return result

    def __filter_master_version(self, version_to_filter: NodeVersion) -> bool:
        return version_to_filter.node_name == "master" or version_to_filter.node_name == "k8"

    def __filter_node_versions(self, version_to_filter: NodeVersion) -> bool:
        return version_to_filter.node_name == "nodes" or version_to_filter.node_name == "k8"
