import typing
from .AbstractWrapper import AbstractWrapper
from prometheus_client.core import GaugeMetricFamily
from party3rd.kubernetes_internal import K8Application
from party3rd.kubernetes_external import K8Releases
from azure.kubernetes import K8Azure
from gcp.kubernetes import K8GCP
from utils.versions import NodeVersion


class KubernetesWrapper(AbstractWrapper):
    k8_internal: object
    k8_external: object

    def __init__(self, args):
        if not (args.kubernetes and args.kubernetes_token):
            return
        if super().is_aws(args.environment):
            raise BaseException("not supported yet")
        elif super().is_gcp(args.environment):
            self.k8_external = K8GCP(args)
        elif super().is_azure(args.environment):
            self.k8_external = K8Azure(args)
        elif super().is_metal(args.environment):
            self.k8_external = K8Releases()
        self.k8_internal = K8Application(args.kubernetes, args.kubernetes_token)

    def collect(self) -> typing.List[GaugeMetricFamily]:
        if not hasattr(self, "k8_internal"):
            return []
        external_versions = self.k8_external.collect()
        internal_versions = self.k8_internal.collect()
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
