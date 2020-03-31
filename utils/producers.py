import copy
import typing
import logging
from abc import ABC, abstractmethod
from functools import lru_cache
from kubernetes import client
from prometheus_client.core import GaugeMetricFamily
from utils.versions import ApplicationVersion, CHANNELS
from utils.collectors import VersionCollector
from scanners import CollectorFactory, SeverityManager
from utils.verifiers import Severity


class AbstractMetricProducer(ABC):
    active = False
    installation: str
    severity_manager = SeverityManager()

    @abstractmethod
    def __init__(self, installation: str):
        self.installation = installation

    def collect(self) -> typing.List[GaugeMetricFamily]:
        try:
            return self.collect_metrics()
        except Exception:
            logging.warning(f'Error during collecting in {self.__class__}', exc_info=True)
            return []

    @abstractmethod
    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        pass


class CommonMetricProducer(AbstractMetricProducer):
    info_title = "armor_metrics"
    version_title = 'Information about internally used applications versions'
    internal_collector: VersionCollector
    external_collector: VersionCollector

    def __init__(self, installation: str, internal: VersionCollector, external: VersionCollector):
        super().__init__(installation)
        self.internal_collector = internal
        self.external_collector = external
        self.active = True

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        result = []
        try:
            external_versions = self.external_collector.collect()
        except Exception:
            logging.error("Error appears during external version gathering", exc_info=True)
            return result
        try:
            internal_versions = self.internal_collector.collect()
        except Exception:
            logging.error("Error appears during external version gathering", exc_info=True)
            return result
        for internal_version in internal_versions:
            result += self.extract_metrics(internal_version, external_versions)
        return result

    def extract_metrics(self, app_version: ApplicationVersion, versions: typing.Iterator[ApplicationVersion]) -> \
            typing.List[GaugeMetricFamily]:
        label_titles = ["installation", "application", "node", "pod", "channel", "severity"]
        app_name = app_version.app
        node_name = app_version.node_name
        pod_name = app_version.pod_name
        diff = self.exctract_differences(app_version, versions)
        result = []
        for channel in CHANNELS:
            channel_metric = GaugeMetricFamily(self.info_title, self.version_title, labels=label_titles)
            value = diff.get_channel_version(channel)
            severity = self.severity_manager.get_severity(app_version, channel, value)
            if severity == Severity.NONE:
                continue
            channel_metric.add_metric([self.installation, app_name, node_name, pod_name, channel.value, severity.value],
                                      value)
            result.append(channel_metric)
        return result

    def exctract_differences(self, version_to_check: ApplicationVersion,
                             all_versions: typing.Iterator[ApplicationVersion]) -> ApplicationVersion:
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
            if major_match and minor_match and release_match and version.build > result.build:
                result.build = version.build
        return result - version_to_check


class KubernetesMetricProducer(CommonMetricProducer):

    def __init__(self, installation: str, factory: CollectorFactory):
        k8_internal = factory.instantiate_collector("party3rd.cloud_native.k8")
        k8_external = factory.instantiate_k8_service_collector()
        super().__init__(installation, k8_internal, k8_external)

    @lru_cache(maxsize=128, typed=False)
    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        if not self.active:
            return []
        external_versions = self.external_collector.collect()
        internal_versions = self.internal_collector.collect()
        result = []
        for internal_version in internal_versions:
            is_master = internal_version.node_name == "master"
            filter_function = self.__filter_master_version if is_master else self.__filter_node_versions
            result += super().extract_metrics(internal_version, filter(filter_function, external_versions))
        return result

    def __filter_master_version(self, version_to_filter: ApplicationVersion) -> bool:
        return version_to_filter.node_name == "master" or version_to_filter.node_name == "k8"

    def __filter_node_versions(self, version_to_filter: ApplicationVersion) -> bool:
        return version_to_filter.node_name == "nodes" or version_to_filter.node_name == "k8"


class ApplicationMetricProducer(AbstractMetricProducer):
    factory: CollectorFactory
    constant_version_collector = "utils.constant"

    def __init__(self, installation: str, factory: CollectorFactory):
        super().__init__(installation)
        self.factory = factory

    @lru_cache(maxsize=128, typed=False)
    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        applications = self.extract_applications()
        result = []
        for application in applications.items():
            application_name = application[0]
            for application_version in application[1]:
                internal = self.factory.instantiate_collector(self.constant_version_collector, application_version)
                external = self.factory.instantiate_collector(application_name)
                # todo each collector separatly in separate thread? by application in order to cache response!
                result += CommonMetricProducer(self.installation, internal, external).collect_metrics()
        return result

    def extract_applications(self) -> typing.Dict[str, typing.List[ApplicationVersion]]:
        ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
        result = dict()
        for i in ret.items:
            if i.metadata.annotations is None:
                continue
            for annotation in i.metadata.annotations.keys():
                # template armor.io/{app_group}/{app_type}/{application} : "armor.io/gcp.java_client.spanner"
                if "armor.io" not in annotation:
                    continue
                application = annotation.split(sep="/", maxsplit=1)[1]
                if application not in result:
                    result[application] = []
                version = i.metadata.annotations[annotation]
                result[application].append(ApplicationVersion(application, version, i.spec.node_name, i.metadata.name))
                logging.info(f'Application {application} with version {version} on pod {i.metadata.name} was detected')
        return result
