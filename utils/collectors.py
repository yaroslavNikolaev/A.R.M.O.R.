import ssl, typing, json, logging, abc
from http.client import HTTPSConnection
from cachetools.func import ttl_cache
from pyquery import PyQuery
from utils.versions import ApplicationVersion, ZERO_VERSION
from utils.configuration import Configuration


class VersionCollector(abc.ABC):
    singleton = True

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

    @ttl_cache(maxsize=16, ttl=200)
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
    singleton = False

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
    pager = "/repositories/{}/releases?page={}"
    header: dict
    release_pages_to_handle = 2  # =release_pages_to_handle*30 releases
    releases: str

    def __init__(self, config: Configuration, owner: str, repo: str):
        super().__init__(config)
        self.releases = self.template.format(owner, repo)
        self.header = {'Authorization': 'Basic ' + config.gh_auth(), "User-Agent": "PostmanRuntime/7.23.0"}

    @ttl_cache(maxsize=16, ttl=200)
    def collect(self) -> typing.List[ApplicationVersion]:
        connection = HTTPSConnection(host=self.git, context=ssl._create_unverified_context())
        connection.request(url=self.releases, method="GET", headers=self.header)
        response = connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        result = self.collect_gh_releases(resp)
        last_page_number = 1
        tracker_number = 0
        for head in response.getheaders():
            # why don't they introduced 3 headers instead of this bullshit?
            if head[0] == 'link':
                last_page = str(head[1]).split(',')[1].split(";")[0].split("/")
                last_page_number = int(last_page[len(last_page) - 1].split("=")[1][:-1])
                tracker_number = last_page[4]
        finish = last_page_number if last_page_number < self.release_pages_to_handle else self.release_pages_to_handle
        for page in range(2, finish + 1):
            url = self.pager.format(tracker_number, page)
            connection.request(url=url, method="GET", headers=self.header)
            response = connection.getresponse()
            resp = json.loads(response.read().decode("utf-8"))
            result += self.collect_gh_releases(resp)
        return result

    def collect_gh_releases(self, releases) -> typing.List[ApplicationVersion]:
        result = []
        app = self.get_application_name()
        for release in releases:
            try:
                result.append(ApplicationVersion(app, release['tag_name']))
            except (ValueError, TypeError, IndexError):
                logging.warning(f"Release {release['tag_name']} has incorrect version structure for GH {app}")
                continue
        return result


class MockCollector(VersionCollector):
    def __init__(self, config: Configuration, *args):
        super().__init__(config, *args)

    def collect(self) -> typing.List[ApplicationVersion]:
        return [ZERO_VERSION]

    @staticmethod
    def get_application_name() -> str:
        return "mock"
