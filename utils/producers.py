import copy
import typing
import logging
from abc import ABC, abstractmethod
from kubernetes import client
from prometheus_client.core import GaugeMetricFamily
from utils.versions import ApplicationVersion, CHANNELS
from utils.collectors import VersionCollector
from scanners import CollectorFactory, SeverityManager
from utils.verifiers import Severity, SEVERITIES


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


class SeverityFactorProducer(AbstractMetricProducer):
    metrics: typing.List[GaugeMetricFamily]
    info_title = "severity_factor"
    version_title = "Special metric. Armor uses it in prometheus queries. "
    label_titles = ["installation", "severity"]
    # 1,10,100,1000
    base = 10

    def __init__(self, installation: str):
        super().__init__(installation)
        self.metrics = []
        for severity in SEVERITIES:
            value = pow(self.base, len(SEVERITIES) - len(self.metrics) - 1)
            severity_factor_metric = GaugeMetricFamily(self.info_title, self.version_title, labels=self.label_titles)
            severity_factor_metric.add_metric([self.installation, severity.value], value)
            self.metrics.append(severity_factor_metric)

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        return self.metrics


class CommonMetricProducer(AbstractMetricProducer):
    info_title = "armor_metrics"
    version_title = 'Information about internally used applications versions'
    label_titles = ["installation", "application", "resource", "name", "channel", "severity"]
    internal_collector: VersionCollector
    external_collector: VersionCollector
    ex_clazz: str
    in_clazz: str

    def __init__(self, installation: str, internal: VersionCollector, external: VersionCollector):
        super().__init__(installation)
        self.internal_collector = internal
        self.external_collector = external
        self.active = True
        self.ex_clazz = str(self.external_collector.__class__)
        self.in_clazz = str(self.internal_collector.__class__)

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        result = []
        try:
            external_versions = self.external_collector.collect()
        except Exception:
            logging.error(f"Error appears during external version gathering {self.ex_clazz}", exc_info=True)
            return []
        try:
            internal_versions = self.internal_collector.collect()
        except Exception:
            logging.error(f"Error appears during internal version gathering {self.in_clazz}", exc_info=True)
            return []
        for internal_version in internal_versions:
            result += self.extract_metrics(internal_version, external_versions)
        return result

    def extract_metrics(self, app_version: ApplicationVersion, versions: typing.Iterator[ApplicationVersion]) -> \
            typing.List[GaugeMetricFamily]:
        app_name = app_version.app
        resource = app_version.resource
        name = app_version.resource_name
        diff = self.exctract_differences(app_version, versions)
        result = []
        for channel in CHANNELS:
            channel_metric = GaugeMetricFamily(self.info_title, self.version_title, labels=self.label_titles)
            value = diff.get_channel_version(channel)
            severity = self.severity_manager.get_severity(app_version, channel, value)
            if severity == Severity.NONE:
                continue
            channel_metric.add_metric([self.installation, app_name, resource, name, channel.value, severity.value],
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

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        if not self.active:
            return []
        external_versions = self.external_collector.collect()
        internal_versions = self.internal_collector.collect()
        result = []
        for internal_version in internal_versions:
            is_master = internal_version.resource_name == "master"
            filter_function = self.__filter_master_version if is_master else self.__filter_node_versions
            result += super().extract_metrics(internal_version, filter(filter_function, external_versions))
        return result

    def __filter_master_version(self, version_to_filter: ApplicationVersion) -> bool:
        return version_to_filter.resource_name == "master" or version_to_filter.resource_name == "k8"

    def __filter_node_versions(self, version_to_filter: ApplicationVersion) -> bool:
        return version_to_filter.resource_name == "nodes" or version_to_filter.resource_name == "k8"


class ApplicationMetricProducer(AbstractMetricProducer, ABC):
    factory: CollectorFactory
    constant_version_collector = "utils.collectors.constant"
    armor = "armor.io"

    def __init__(self, installation: str, factory: CollectorFactory):
        super().__init__(installation)
        self.factory = factory

    def collect_metrics(self) -> typing.List[GaugeMetricFamily]:
        result = []
        for application in self.extract_applications_versions().items():
            application_name = application[0]
            for application_version in application[1]:
                internal = self.factory.instantiate_collector(self.constant_version_collector, application_version)
                external = self.factory.instantiate_collector(application_name)
                result += CommonMetricProducer(self.installation, internal, external).collect_metrics()
        return result

    def extract_applications_versions(self) -> typing.Dict[str, typing.List[ApplicationVersion]]:
        result = dict()
        for item in self.get_k8_resources():
            name = item.metadata.name
            versions = []
            if item.metadata.annotations is not None:
                versions += self.parse_annotations(item.metadata.annotations, name)
            if hasattr(item.spec, "template") and \
                    item.spec.template.metadata is not None and \
                    item.spec.template.metadata.annotations is not None:
                versions += self.parse_annotations(item.spec.template.metadata.annotations, name)

            for version in versions:
                apps = set()
                length_before = len(apps)
                apps.add(version.app)
                if length_before == len(apps):
                    logging.warning(f"{version.app} defined twice in spec only first value will be taken")
                    continue
                if version.app not in result:
                    result[version.app] = []
                result[version.app].append(version)
        return result

    @abstractmethod
    def get_resource_type(self) -> str:
        pass

    @abstractmethod
    def get_k8_resources(self) -> typing.Iterable:
        pass

    def parse_annotations(self, annotations: dict, name: str) -> typing.List[ApplicationVersion]:
        result = []
        resource = self.get_resource_type()
        for annotation in annotations.keys():
            # template armor.io/{app_group}/{app_type}/{application} : "armor.io/gcp.java_client.spanner"
            if self.armor not in annotation:
                continue
            application = annotation.split(sep="/", maxsplit=1)[1]
            version = annotations[annotation]
            result.append(ApplicationVersion(application, version, resource, name))
            logging.info(f'{resource} {name} with application {application}:{version} was detected')
        return result


class DaemonSetMetricProducer(ApplicationMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.AppsV1Api().list_daemon_set_for_all_namespaces(watch=False).items

    def get_resource_type(self) -> str:
        return "deamonset"


class DeploymentMetricProducer(ApplicationMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.AppsV1Api().list_deployment_for_all_namespaces(watch=False).items

    def get_resource_type(self) -> str:
        return "deployment"


class StatefulSetMetricProducer(ApplicationMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.AppsV1Api().list_stateful_set_for_all_namespaces(watch=False).items

    def get_resource_type(self) -> str:
        return "statefulset"


class NamespaceMetricProducer(ApplicationMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.CoreV1Api().list_namespace(watch=False).items

    def get_resource_type(self) -> str:
        return "namespace"


class NodeMetricProducer(ApplicationMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.CoreV1Api().list_namespace(watch=False).items

    def get_resource_type(self) -> str:
        return "node"
