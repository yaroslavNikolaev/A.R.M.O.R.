import typing
import re
from pyquery import PyQuery
from utils.collectors import VersionCollector
from utils.versions import NodeVersion
from http.client import HTTPSConnection


class FilebeatCollector(VersionCollector):
    elastic = "www.elastic.co"
    versions = "/guide/en/beats/libbeat/current/release-notes.html"
    artifact = "filebeat"
    stable_versions = '[a-zA-Z]*\d+\.\d+\.\d+$'

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.elastic)
        connection.request(url=self.versions, method="GET")
        response = connection.getresponse()
        parser = PyQuery(response.read().decode("utf-8"))
        releases = parser.find(".xref").text().lstrip().split(" ")
        result = []
        for release in releases:
            if not re.search(self.stable_versions, release):
                continue
            release_version = NodeVersion(release, self.artifact)
            result.append(release_version)

        return result
