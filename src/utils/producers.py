import copy, typing, logging, concurrent.futures
from cachetools.func import ttl_cache
from abc import ABC, abstractmethod
from kubernetes import client
from utils.versions import ApplicationVersion, CHANNELS, Channel
from utils.collectors import VersionCollector
from scanners import CollectorFactory, SeverityManager
from utils.verifiers import Severity

MIN_TTL = 601


class Metric(object):
    source: ApplicationVersion
    target: ApplicationVersion
    severity: Severity
    diff: int

    def __init__(self, source: ApplicationVersion, target: ApplicationVersion, severity: Severity, diff):
        self.source = source
        self.target = target
        self.severity = severity
        self.diff = diff


class AbstractMetricProducer(ABC):
    active = False
    cluster: str
    severity_manager = SeverityManager()

    @abstractmethod
    def __init__(self, cluster: str):
        self.cluster = cluster

    def collect(self) -> typing.List[Metric]:
        try:
            return self._collect_metrics()
        except Exception:
            logging.warning(f'Error during collecting in {self.__class__}', exc_info=True)
            return []

    @abstractmethod
    def _collect_metrics(self) -> typing.List[Metric]:
        pass


class CommonMetricProducer(AbstractMetricProducer):
    internal_collector: VersionCollector
    external_collector: VersionCollector
    ex_clazz: str
    in_clazz: str

    def __init__(self, cluster: str, internal: VersionCollector, external: VersionCollector):
        super().__init__(cluster)
        self.internal_collector = internal
        self.external_collector = external
        self.active = True
        self.ex_clazz = str(self.external_collector.__class__)
        self.in_clazz = str(self.internal_collector.__class__)

    def _collect_metrics(self) -> typing.List[Metric]:
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
            result += self._extract_metrics(internal_version, external_versions)
        return result

    def _extract_metrics(self, app_version: ApplicationVersion, versions: typing.List[ApplicationVersion]) -> \
            typing.List[Metric]:
        diff = self.extract_channel_top_versions(app_version, versions)
        result = []
        for channel, channel_version in diff.items():
            value = channel_version.get_channel_version(channel) - app_version.get_channel_version(channel)
            severity = self.severity_manager.get_severity(app_version, channel, value)
            if severity == Severity.NONE:
                continue
            metric = Metric(app_version, channel_version, severity, value)
            result.append(metric)
        return result

    @staticmethod
    def extract_channel_top_versions(version_to_check: ApplicationVersion,
                                     all_versions: typing.List[ApplicationVersion]) \
            -> typing.Dict[Channel, ApplicationVersion]:
        result = dict()
        for version in all_versions:
            diff = version - version_to_check
            top_channel = diff.get_first_positive_valid_channel()
            if top_channel is None:
                continue
            if top_channel not in result:
                result[top_channel] = version
            else:
                diff = version - result[top_channel]
                if diff.get_first_positive_valid_channel() is not None:
                    result[top_channel] = version
        return result


class KubernetesMetricProducer(CommonMetricProducer):
    k8 = "party3rd.cloud_native.k8"
    default = "party3rd.cloud_native.kubernetes"
    cloud_collectors = {
        "gcp": "gcp.kubernetes.gke",
        "azure": "az.kubernetes.aks",
        "aws": "aws.kubernetes.eks"
    }

    def __init__(self, cluster: str, factory: CollectorFactory, cloud: str):
        k8_internal = factory.instantiate_collector(self.k8)
        k8_external = factory.instantiate_collector(self.cloud_collectors.get(cloud, self.default))
        super().__init__(cluster, k8_internal, k8_external)

    @ttl_cache(ttl=MIN_TTL + 443, maxsize=4)
    def _collect_metrics(self) -> typing.List[Metric]:
        if not self.active:
            return []
        external_versions = self.external_collector.collect()
        internal_versions = self.internal_collector.collect()
        result = []
        for internal_version in internal_versions:
            is_master = internal_version.resource_name == "master"
            filter_function = self.__filter_master_version if is_master else self.__filter_node_versions
            result += super()._extract_metrics(internal_version, filter(filter_function, external_versions))
        return result

    def __filter_master_version(self, version_to_filter: ApplicationVersion) -> bool:
        return version_to_filter.resource_name == "master" or version_to_filter.resource_name == "k8"

    def __filter_node_versions(self, version_to_filter: ApplicationVersion) -> bool:
        return version_to_filter.resource_name == "nodes" or version_to_filter.resource_name == "k8"


class ApplicationMetricProducer(AbstractMetricProducer, ABC):
    factory: CollectorFactory
    application: str
    versions: typing.List[ApplicationVersion]
    constant_version_collector = "utils.collectors.constant"

    def __init__(self, cluster: str, app: str, versions: typing.List[ApplicationVersion],
                 factory: CollectorFactory):
        super().__init__(cluster)
        self.application = app
        self.versions = versions
        self.factory = factory

    def _collect_metrics(self) -> typing.List[Metric]:
        result = []
        for application_version in self.versions:
            internal = self.factory.instantiate_collector(self.constant_version_collector, [application_version])
            external = self.factory.instantiate_collector(self.application)
            result += CommonMetricProducer(self.cluster, internal, external)._collect_metrics()
        return result


class KubernetesResourceMetricProducer(AbstractMetricProducer, ABC):
    factory: CollectorFactory
    armor = "armor.io"

    def __init__(self, cluster: str, factory: CollectorFactory):
        super().__init__(cluster)
        self.factory = factory

    def _collect_metrics(self) -> typing.List[Metric]:
        result = []
        futures = []
        # todo think about necessity of this action.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for application in self.extract_applications_versions().items():
                versions = application[1]
                app = application[0]
                app_collector = ApplicationMetricProducer(self.cluster, app, versions, self.factory)
                futures.append(executor.submit(app_collector.collect))
            for future in futures:
                result += future.result()
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


class DaemonSetMetricProducer(KubernetesResourceMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.AppsV1Api().list_daemon_set_for_all_namespaces(watch=False).items

    def get_resource_type(self) -> str:
        return "deamonset"

    @ttl_cache(ttl=MIN_TTL + 307, maxsize=4)
    def _collect_metrics(self) -> typing.List[Metric]:
        return super()._collect_metrics()


class DeploymentMetricProducer(KubernetesResourceMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.AppsV1Api().list_deployment_for_all_namespaces(watch=False).items

    def get_resource_type(self) -> str:
        return "deployment"

    @ttl_cache(ttl=MIN_TTL, maxsize=4)
    def _collect_metrics(self) -> typing.List[Metric]:
        return super()._collect_metrics()


class StatefulSetMetricProducer(KubernetesResourceMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.AppsV1Api().list_stateful_set_for_all_namespaces(watch=False).items

    def get_resource_type(self) -> str:
        return "statefulset"

    @ttl_cache(ttl=MIN_TTL + 61, maxsize=4)
    def _collect_metrics(self) -> typing.List[Metric]:
        return super()._collect_metrics()


class NamespaceMetricProducer(KubernetesResourceMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.CoreV1Api().list_namespace(watch=False).items

    def get_resource_type(self) -> str:
        return "namespace"

    @ttl_cache(ttl=MIN_TTL + 227, maxsize=4)
    def _collect_metrics(self) -> typing.List[Metric]:
        return super()._collect_metrics()


class NodeMetricProducer(KubernetesResourceMetricProducer):
    def get_k8_resources(self) -> typing.Iterable:
        return client.CoreV1Api().list_namespace(watch=False).items

    def get_resource_type(self) -> str:
        return "node"

    @ttl_cache(ttl=MIN_TTL + 139, maxsize=4)
    def _collect_metrics(self) -> typing.List[Metric]:
        return super()._collect_metrics()
