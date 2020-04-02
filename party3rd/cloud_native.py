import typing
from kubernetes import client
from utils.versions import ApplicationVersion
from utils.collectors import VersionCollector, GitHubVersionCollector
from utils.configuration import Configuration


class K8Master(VersionCollector):
    @staticmethod
    def get_application_name() -> str:
        return "k8master"

    def __init__(self, config: Configuration):
        super().__init__(config)

    def collect(self) -> typing.List[ApplicationVersion]:
        response = client.VersionApi().get_code_with_http_info()
        master_version = ApplicationVersion("kubernetes", response[0].git_version, "node", "master")
        return [master_version]


class K8Worker(VersionCollector):
    @staticmethod
    def get_application_name() -> str:
        return "k8worker"

    def __init__(self, config: Configuration):
        super().__init__(config)

    def collect(self) -> typing.List[ApplicationVersion]:
        ret = client.CoreV1Api().list_node()
        result = []
        for node in ret.items:
            node_name = node.metadata.name
            release = node.status.node_info.kubelet_version
            node_version = ApplicationVersion("kubernetes", release, "node", node_name)
            result.append(node_version)
        return result


class K8Application(VersionCollector):
    @staticmethod
    def get_application_name() -> str:
        return "k8"

    k8_master: K8Master
    k8_worker: K8Worker

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)
        self.k8_master = K8Master(configuration)
        self.k8_worker = K8Worker(configuration)

    def collect(self) -> typing.List[ApplicationVersion]:
        result = []
        result += self.k8_master.collect()
        result += self.k8_worker.collect()
        return result


class K8VersionCollector(GitHubVersionCollector):
    owner = "kubernetes"
    repo = "kubernetes"

    @staticmethod
    def get_application_name() -> str:
        return "kubernetes"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class IngressNginxVersionCollector(GitHubVersionCollector):
    owner = "kubernetes"
    repo = "ingress-nginx"

    @staticmethod
    def get_application_name() -> str:
        return "ingress-nginx"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class IngressGceVersionCollector(GitHubVersionCollector):
    owner = "kubernetes"
    repo = "ingress-gce"

    @staticmethod
    def get_application_name() -> str:
        return "ingress-gce"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class ArmorCollector(VersionCollector):
    version: typing.List[ApplicationVersion]

    def collect(self) -> typing.List[ApplicationVersion]:
        return self.version

    @staticmethod
    def get_application_name() -> str:
        return "armor"

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.version = [ApplicationVersion(self.get_application_name(), config.version())]


class PrometheusVersionCollector(GitHubVersionCollector):
    owner = "prometheus"
    repo = "prometheus"

    @staticmethod
    def get_application_name() -> str:
        return "prometheus"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class AlertManagerVersionCollector(GitHubVersionCollector):
    owner = "prometheus"
    repo = "alertmanager"

    @staticmethod
    def get_application_name() -> str:
        return "alertmanager"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class NodeExporterVersionCollector(GitHubVersionCollector):
    owner = "prometheus"
    repo = "node_exporter"

    @staticmethod
    def get_application_name() -> str:
        return "node_exporter"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)
