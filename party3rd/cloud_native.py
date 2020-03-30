import typing
import re
import ssl
from kubernetes import client
from utils.versions import NodeVersion
from utils.collectors import VersionCollector, singleton
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

    def collect(self) -> typing.List[NodeVersion]:
        response = client.VersionApi().get_code_with_http_info()
        master_version = NodeVersion("kubernetes", response[0].git_version, "master")
        return [master_version]


@singleton
class K8Worker(VersionCollector):
    @staticmethod
    def get_application_name() -> str:
        return "k8worker"

    def __init__(self, config: Configuration):
        super().__init__(config)

    def collect(self) -> typing.List[NodeVersion]:
        ret = client.CoreV1Api().list_node()
        result = []
        for node in ret.items:
            node_name = node.metadata.name
            release = node.status.node_info.kubelet_version
            node_version = NodeVersion("kubernetes", release, node_name)
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

    def collect(self) -> typing.List[NodeVersion]:
        result = []
        result += self.k8_master.collect()
        result += self.k8_worker.collect()
        return result


@singleton
class K8Releases(VersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "kubernetes"

    git = "github.com"
    kubernetes_release = "/kubernetes/kubernetes/releases"
    stable_versions = '^v\d+\.\d+\.\d+$'

    def __init__(self, config: Configuration):
        super().__init__(config)

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.git, context=ssl._create_unverified_context())
        connection.request(url=self.kubernetes_release, method="GET")
        response = connection.getresponse()
        parser = PyQuery(response.read().decode("utf-8"))
        releases = parser("[href]")("[title]").text().lstrip().split(" ")
        # todo gather as much as possible versions
        result = []
        for release in releases:
            if not re.search(self.stable_versions, release):
                continue
            release_version = NodeVersion("kubernetes", release, "k8")
            result.append(release_version)
            break

        return result


@singleton
class ArmorCollector(VersionCollector):
    version: typing.List[NodeVersion]

    def collect(self) -> typing.List[NodeVersion]:
        return self.version

    @staticmethod
    def get_application_name() -> str:
        return "armor"

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.version = [NodeVersion(self.get_application_name(), config.version())]
