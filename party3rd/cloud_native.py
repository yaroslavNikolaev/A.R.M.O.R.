import typing
import re
import ssl
from kubernetes import client
from utils.versions import ApplicationVersion
from utils.collectors import VersionCollector, GitHubVersionCollector, singleton
from utils.configuration import Configuration
from http.client import HTTPSConnection
from pyquery import PyQuery


@singleton
class K8Master(VersionCollector):
    @staticmethod
    def get_application_name() -> str:
        return "k8master"

    def __init__(self, config: Configuration, ):
        super().__init__(config)

    def collect(self) -> typing.List[ApplicationVersion]:
        response = client.VersionApi().get_code_with_http_info()
        master_version = ApplicationVersion("kubernetes", response[0].git_version, "master")
        return [master_version]


@singleton
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
            node_version = ApplicationVersion("kubernetes", release, node_name)
            result.append(node_version)
        return result


@singleton
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


@singleton
class K8Releases(GitHubVersionCollector):
    owner = "kubernetes"
    repo = "kubernetes"

    @staticmethod
    def get_application_name() -> str:
        return "kubernetes"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


@singleton
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
