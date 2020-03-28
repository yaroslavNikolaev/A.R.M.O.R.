import typing
from kubernetes import client
from utils.versions import NodeVersion
from utils.collectors import VersionCollector
from utils.configuration import Configuration


class K8Master(VersionCollector):
    def __init__(self, config: Configuration, ):
        super().__init__(config)

    def collect(self) -> typing.List[NodeVersion]:
        response = client.VersionApi().get_code_with_http_info()
        master_version = NodeVersion(response[0].git_version, "master")
        return [master_version]


class K8Worker(VersionCollector):
    def __init__(self, config: Configuration):
        super().__init__(config)

    def collect(self) -> typing.List[NodeVersion]:
        ret = client.CoreV1Api().list_node()
        result = []
        for node in ret.items:
            name = node.metadata.name
            release = node.status.node_info.kubelet_version
            node_version = NodeVersion(release, name)
            result.append(node_version)
        return result


class K8Application(VersionCollector):
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
