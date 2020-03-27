import abc
import copy
import typing
from prometheus_client.core import GaugeMetricFamily
from utils.versions import NodeVersion
from utils.collectors import VersionCollector

EMPTY_ARRAY = ()


class AbstractWrapper(abc.ABC):
    active = False
    installation: str

    def __init__(self, installation: str):
        self.installation = installation

    @abc.abstractmethod
    def collect(self) -> typing.List[GaugeMetricFamily]:
        pass


class CommonWrapper(AbstractWrapper):
    internal_collector: VersionCollector
    external_collector: VersionCollector

    def __init__(self, installation: str, internal: VersionCollector, external: VersionCollector):
        super().__init__(installation)
        self.internal_collector = internal
        self.external_collector = external
        self.active = True

    def collect(self) -> typing.List[GaugeMetricFamily]:
        external_versions = self.external_collector.collect()
        internal_versions = self.internal_collector.collect()
        result = []
        for internal_version in internal_versions:
            result += self.extract_metrics(internal_version, external_versions)
        return result

    def extract_metrics(self, app_version: NodeVersion, versions: typing.Iterator[NodeVersion]) -> \
            typing.List[GaugeMetricFamily]:
        diff = self.exctract_differences(app_version, versions)
        major = GaugeMetricFamily("k8_info", 'Kubernetes version',
                                  labels=["installation", "application", "node", "channel"])
        major.add_metric([self.installation, "kubernetes", app_version.node_name, "major"], diff.major)
        minor = GaugeMetricFamily("k8_info", 'Kubernetes version',
                                  labels=["installation", "application", "node", "channel"])
        minor.add_metric([self.installation, "kubernetes", app_version.node_name, "minor"], diff.minor)
        release = GaugeMetricFamily("k8_info", 'Kubernetes version',
                                    labels=["installation", "application", "node", "channel"])
        release.add_metric([self.installation, "kubernetes", app_version.node_name, "release"], diff.release)
        built = GaugeMetricFamily("k8_info", 'Kubernetes version',
                                  labels=["installation", "application", "node", "channel"])
        built.add_metric([self.installation, "kubernetes", app_version.node_name, "built"], diff.built)
        return [major, minor, release, built]

    def exctract_differences(self, version_to_check: NodeVersion,
                             all_versions: typing.Iterator[NodeVersion]) -> NodeVersion:
        result = copy.copy(version_to_check)
        for version in all_versions:
            major_match = version.major == version_to_check.major
            minor_match = version.minor == version_to_check.minor
            release_match = version.release == version_to_check.release
            if version.major > result.major:
                result.major = version.major
            if major_match and version.minor > result.minor:
                result.minor = version.minor
            if major_match and minor_match and version.release > result.release:
                result.release = version.release
            if major_match and minor_match and release_match and version.built > result.built:
                result.built = version.built
        return result - version_to_check


class KubernetesWrapper(CommonWrapper):

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