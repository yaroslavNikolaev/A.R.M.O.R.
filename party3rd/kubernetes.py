from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from http.client import HTTPSConnection
from pyquery import PyQuery
import json
import ssl
import re


class _k8_master(object):
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
        versions = str(resp['gitVersion']).split(".")
        metric = GaugeMetricFamily("k8_master_info", 'Kubernetes master version',
                                   labels=["major", "minor", "release", "version"])
        metric.add_metric([versions[0][1:len(versions[0])], versions[1], versions[2], resp['gitVersion']], 1)
        return [metric]


class _k8_worker(object):
    connection: HTTPSConnection
    auth: map

    def __init__(self, endpoint: str, token: str):
        self.connection = HTTPSConnection(host=endpoint, context=ssl._create_unverified_context())
        self.auth = {"Authorization": "Bearer " + token}
        pass

    def collect(self):
        self.connection.request(url="/api/v1/nodes", method="GET", headers=self.auth)
        response = self.connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        result = []
        for node in resp['items']:
            name = node['metadata']['name']
            versions = str(node['status']['nodeInfo']['kubeletVersion']).split(".")
            metric = GaugeMetricFamily("k8_worker_info", 'Kubernetes worker version',
                                       labels=["major", "minor", "release", "version", "node"])
            metric.add_metric(
                [versions[0][1:len(versions[0])], versions[1], versions[2], node['status']['nodeInfo']['kubeletVersion'], name], 1)
            result += [metric]
        return result


class _k8_release(object):
    git = "github.com"
    kubernetes_release = "/kubernetes/kubernetes/releases"
    stable_versions = '^v\d+\.\d+\.\d+$'

    def __init__(self):
        pass

    def collect(self):
        connection = HTTPSConnection(host=self.git, context=ssl._create_unverified_context())
        connection.request(url=self.kubernetes_release, method="GET")
        response = connection.getresponse()
        parser = PyQuery(response.read().decode("utf-8"))
        page_versions = parser("[href]")("[title]").text()
        releases = page_versions.lstrip().split(" ")
        # not necessary last version in this page -> do find it/
        result = []
        for release in releases:
            if not re.search(self.stable_versions, release):
                continue
            versions = release.split(".")
            metric = GaugeMetricFamily("k8_release_info", 'Kubernetes version', labels=["major", "minor", "release", "version"])
            metric.add_metric([versions[0][1:len(versions[0])], versions[1], versions[2], release], 1)
            # metric = GaugeMetricFamily("k8_info", 'Kubernetes version', labels=['k8_releases'])
            # metric.add_metric(["major"], versions[0][1:len(versions[0])])
            # metric.add_metric(["minor"], versions[1])
            # metric.add_metric(["release"], versions[2])
            result += [metric]

        return result


class K8(object):
    k8_master: _k8_master
    k8_worker: _k8_worker
    k8_release = _k8_release()

    def __init__(self, endpoint: str, token: str):
        self.k8_master = _k8_master(endpoint, token)
        self.k8_worker = _k8_worker(endpoint, token)

    def collect(self):
        result = []
        # todo diff.
        result += self.k8_release.collect()
        result += self.k8_master.collect()
        result += self.k8_worker.collect()
        return result
