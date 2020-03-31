import abc
import ssl
import typing
import json
import logging
from http.client import HTTPSConnection
from pyquery import PyQuery
from utils.versions import ApplicationVersion, ZERO_VERSION
from utils.configuration import Configuration


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


class VersionCollector(abc.ABC):

    @abc.abstractmethod
    def __init__(self, config: Configuration, *args):
        pass

    @abc.abstractmethod
    def collect(self) -> typing.List[ApplicationVersion]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_application_name() -> str:
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

    def collect(self) -> typing.List[ApplicationVersion]:
        connection = HTTPSConnection(host=self.maven)
        connection.request(url=self.versions, method="GET")
        response = connection.getresponse()
        parser = PyQuery(response.read().decode("utf-8"))
        releases = parser.find(".release").text().lstrip().split(" ")
        result = []
        for release in releases:
            release_version = ApplicationVersion(self.get_application_name(), release)
            result.append(release_version)

        return result


class ConstantVersionCollector(VersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "constant"

    version: ApplicationVersion

    def __init__(self, config: Configuration, version: ApplicationVersion):
        super().__init__(config)
        self.version = version

    def collect(self) -> typing.List[ApplicationVersion]:
        return [self.version]


class GitHubVersionCollector(VersionCollector, abc.ABC):
    git = "api.github.com"
    template = "/repos/{}/{}/releases"
    releases: str
    header = {"User-Agent": "PostmanRuntime/7.23.0"}

    def __init__(self, config: Configuration, owner: str, repo: str):
        super().__init__(config)
        self.releases = self.template.format(owner, repo)

    def collect(self) -> typing.List[ApplicationVersion]:
        connection = HTTPSConnection(host=self.git, context=ssl._create_unverified_context())
        connection.request(url=self.releases, method="GET", headers=self.header)
        response = connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        result = []
        app = self.get_application_name()
        for release in resp:
            try:
                result.append(ApplicationVersion(app, release['tag_name']))
            except ValueError:
                logging.warning(f"Release {release['tag_name']} has incorrect version structure for GH {app}")
                continue
        return result


@singleton
class MockCollector(VersionCollector):
    def __init__(self, config: Configuration, *args):
        super().__init__(config, *args)

    def collect(self) -> typing.List[ApplicationVersion]:
        return [ZERO_VERSION]

    @staticmethod
    def get_application_name() -> str:
        return "mock"
