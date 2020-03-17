import abc
import copy
import typing
from prometheus_client.core import GaugeMetricFamily
from utils.versions import NodeVersion
from utils.versions import VersionCollector

EMPTY_ARRAY = ()


class AbstractWrapper(abc.ABC):
    active = False
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    BARE_METAL = "metal"
    installation: str

    def __init__(self, installation: str):
        self.installation = installation

    def is_aws(self, environment: str) -> bool:
        return environment == self.AWS

    def is_azure(self, environment: str) -> bool:
        return environment == self.AZURE

    def is_gcp(self, environment: str) -> bool:
        return environment == self.GCP

    def is_metal(self, environment: str) -> bool:
        return environment == self.BARE_METAL

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
