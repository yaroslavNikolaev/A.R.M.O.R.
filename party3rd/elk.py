import typing
import re
from pyquery import PyQuery
from utils.collectors import VersionCollector, singleton
from utils.configuration import Configuration
from utils.versions import NodeVersion
from http.client import HTTPSConnection


@singleton
class FilebeatCollector(VersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "filebeat"

    def __init__(self, config: Configuration):
        super().__init__(config)

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
            release_version = NodeVersion(self.get_application_name(), release)
            result.append(release_version)

        return result
