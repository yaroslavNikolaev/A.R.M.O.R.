import abc
import copy
import typing
from prometheus_client.core import GaugeMetricFamily
from utils.versions import NodeVersion


class AbstractWrapper(abc.ABC):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    BARE_METAL = "metal"

    @abc.abstractmethod
    def collect(self) -> typing.List[GaugeMetricFamily]:
        pass

    def is_aws(self, environment: str) -> bool:
        return environment == self.AWS

    def is_azure(self, environment: str) -> bool:
        return environment == self.AZURE

    def is_gcp(self, environment: str) -> bool:
        return environment == self.GCP

    def is_metal(self, environment: str) -> bool:
        return environment == self.BARE_METAL

    def __exctract_differences(self, version_to_check: NodeVersion,
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

    def extract_metrics(self, app_version: NodeVersion, versions: typing.Iterator[NodeVersion]) -> \
            typing.List[GaugeMetricFamily]:
        diff = self.__exctract_differences(app_version, versions)
        major = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=["application", "node", "type"])
        major.add_metric(["kubernetes", app_version.node_name, "major"], diff.major)
        minor = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=["application", "node", "type"])
        minor.add_metric(["kubernetes", app_version.node_name, "minor"], diff.minor)
        release = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=["application", "node", "type"])
        release.add_metric(["kubernetes", app_version.node_name, "release"], diff.release)
        built = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=["application", "node", "type"])
        built.add_metric(["kubernetes", app_version.node_name, "built"], diff.built)
        return [major, minor, release, built]


class DummyWrapper(AbstractWrapper):

    def collect(self) -> typing.List[GaugeMetricFamily]:
        return []


DUMMY_SINGLETON_WRAPPER = DummyWrapper()
