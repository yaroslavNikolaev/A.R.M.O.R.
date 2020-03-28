import abc
import typing
from http.client import HTTPSConnection
from pyquery import PyQuery
from utils.versions import NodeVersion
from utils.configuration import Configuration


class VersionCollector(abc.ABC):

    @abc.abstractmethod
    def __init__(self, config: Configuration, *args):
        pass

    @abc.abstractmethod
    def collect(self) -> typing.List[NodeVersion]:
        pass


class MavenCentralVersionCollector(VersionCollector, abc.ABC):
    maven = "mvnrepository.com"
    template = "/artifact/{}/{}"
    versions: str
    artifact: str

    def __init__(self, config: Configuration, group_id: str, artifact_id: str):
        super().__init__(config)
        self.versions = self.template.format(group_id, artifact_id)
        self.artifact = artifact_id

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.maven)
        connection.request(url=self.versions, method="GET")
        response = connection.getresponse()
        parser = PyQuery(response.read().decode("utf-8"))
        releases = parser.find(".release").text().lstrip().split(" ")
        result = []
        for release in releases:
            release_version = NodeVersion(release, self.artifact)
            result.append(release_version)

        return result


class PredefinedVersionCollector(VersionCollector):
    version: NodeVersion

    def __init__(self, config: Configuration, version: NodeVersion):
        super().__init__(config)
        self.version = version

    def collect(self) -> typing.List[NodeVersion]:
        return [self.version]
