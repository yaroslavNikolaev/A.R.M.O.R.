from http.client import HTTPSConnection
from utils.versions import NodeVersion
from utils.collectors import VersionCollector
from pyquery import PyQuery
import re
import typing
import ssl


class K8Releases(VersionCollector):
    git = "github.com"
    kubernetes_release = "/kubernetes/kubernetes/releases"
    stable_versions = '^v\d+\.\d+\.\d+$'

    def __init__(self):
        pass

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.git, context=ssl._create_unverified_context())
        connection.request(url=self.kubernetes_release, method="GET")
        response = connection.getresponse()
        parser = PyQuery(response.read().decode("utf-8"))
        releases = parser("[href]")("[title]").text().lstrip().split(" ")
        # not necessary last version in this page -> do find highest versions and
        result = []
        for release in releases:
            if not re.search(self.stable_versions, release):
                continue
            release_version = NodeVersion(release, "k8")
            result += [release_version]
            break

        return result
