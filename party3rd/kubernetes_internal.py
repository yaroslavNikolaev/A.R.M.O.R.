from http.client import HTTPSConnection
from utils.versions import NodeVersion
from utils.collectors import VersionCollector
import json
import ssl
import typing


class _K8Master(object):
    connection: HTTPSConnection
    auth: map

    def __init__(self, endpoint: str, token: str):
        self.connection = HTTPSConnection(host=endpoint, context=ssl._create_unverified_context())
        self.auth = {"Authorization": "Bearer " + token}
        pass

    def collect(self):
        self.connection.request(url="/version", method="GET", headers=self.auth)
        response = self.connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        node_version = NodeVersion(resp['gitVersion'], "master")
        return [node_version]


class _K8Worker(object):
    connection: HTTPSConnection
    auth: map

    def __init__(self, endpoint: str, token: str):
        self.connection = HTTPSConnection(host=endpoint, context=ssl._create_unverified_context())
        self.auth = {"Authorization": "Bearer " + token}
        pass

    def collect(self) -> typing.List[NodeVersion]:
        self.connection.request(url="/api/v1/nodes", method="GET", headers=self.auth)
        response = self.connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        result = []
        for node in resp['items']:
            name = node['metadata']['name']
            release = node['status']['nodeInfo']['kubeletVersion']
            node_version = NodeVersion(release, name)
            result += [node_version]
        return result


class K8Application(VersionCollector):
    k8_master: _K8Master
    k8_worker: _K8Worker

    def __init__(self, endpoint: str, token: str):
        self.k8_master = _K8Master(endpoint, token)
        self.k8_worker = _K8Worker(endpoint, token)

    def collect(self) -> typing.List[NodeVersion]:
        result = []
        result += self.k8_master.collect()
        result += self.k8_worker.collect()
        return result
