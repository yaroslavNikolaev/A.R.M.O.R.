import typing
from .AbstractWrapper import AbstractWrapper
from prometheus_client.core import GaugeMetricFamily
from party3rd.kubernetes_internal import K8Application
from party3rd.kubernetes_external import K8Releases


class KubernetesWrapper(AbstractWrapper):
    k8_internal: object
    k8_external: object

    def __init__(self, environment: str, endpoint: str, token: str):
        if super().is_aws(environment):
            raise BaseException("not supported yet")
        elif super().is_gcp(environment):
            raise BaseException("not supported yet")
        elif super().is_azure(environment):
            raise BaseException("not supported yet")
        elif super().is_metal(environment):
            self.k8_external = K8Releases()
        self.k8_internal = K8Application(endpoint, token)
        pass

    def collect(self) -> typing.List[GaugeMetricFamily]:
        external_version = self.k8_external.collect()
        internal_versions = self.k8_internal.collect()
        result = []
        for version in internal_versions:
            diff = external_version[0] - version
            metric = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=["application", "node", "armor"])
            metric.add_metric(["kubernetes", version.node_name, "armor"], diff.get_float_value())
            result += [metric]
        return result
