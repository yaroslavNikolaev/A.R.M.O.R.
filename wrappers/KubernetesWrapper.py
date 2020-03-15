import typing
from .AbstractWrapper import AbstractWrapper
from prometheus_client.core import GaugeMetricFamily
from party3rd.kubernetes_internal import K8Application
from party3rd.kubernetes_external import K8Releases
from azure.kubernetes import K8Azure
from gcp.kubernetes import K8GCP


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
        external_version = self.k8_external.collect()
        internal_versions = self.k8_internal.collect()
        result = []
        for version in internal_versions:
            diff = external_version[0] - version
            metric = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=["application", "node", "armor"])
            metric.add_metric(["kubernetes", version.node_name, "armor"], diff.get_float_value())
            result += [metric]
        return result
