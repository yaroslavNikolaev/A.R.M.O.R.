import typing, logging, abc, requests
from cachetools.func import ttl_cache
from pyquery import PyQuery
from utils.versions import ApplicationVersion, ZERO_VERSION
from utils.configuration import Configuration


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
    maven = "https://mvnrepository.com/artifact/{}/{}"
    versions: str

    def __init__(self, config: Configuration, group_id: str, artifact_id: str):
        super().__init__(config)
        self.versions = self.maven.format(group_id, artifact_id)

    # 1 hour
    @ttl_cache(maxsize=16, ttl=3600)
    def collect(self) -> typing.List[ApplicationVersion]:
        response = requests.get(self.versions)
        releases = PyQuery(response.text).find(".release").text().lstrip().split(" ")
        result = []
        for release in releases:
            release_version = ApplicationVersion(self.get_application_name(), release)
            result.append(release_version)
        return result


class ConstantVersionsCollector(VersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "constant"

    versions: typing.List[ApplicationVersion]

    def __init__(self, config: Configuration, versions: typing.List[ApplicationVersion]):
        super().__init__(config)
        self.versions = versions

    def collect(self) -> typing.List[ApplicationVersion]:
        return self.versions


class GitHubVersionCollector(VersionCollector, abc.ABC):
    git_release = "https://api.github.com/repos/{}/{}/releases"
    git_release_pager = "https://api.github.com/repositories/{}/releases?page={}"
    releases: str
    header: dict
    release_pages_to_handle = 2  # =release_pages_to_handle*30 releases

    def __init__(self, config: Configuration, owner: str, repo: str):
        super().__init__(config)
        self.releases = self.git_release.format(owner, repo)
        self.header = {'Authorization': 'Basic ' + config.gh_auth(), "User-Agent": "PostmanRuntime/7.23.0"}

    # 1 hour
    @ttl_cache(maxsize=16, ttl=3600)
    def collect(self) -> typing.List[ApplicationVersion]:
        logging.warning(f"Collect GH data {self.get_application_name()}")
        response = requests.get(self.releases, headers=self.header)
        if response.status_code != 200:
            logging.warning(f"Collect GH data response: {response.status_code}")
            return []
        resp = response.json()
        result = self.collect_gh_releases(resp)
        release_details = self.extract_release_details(response)
        last_page = release_details[1]
        finish = last_page if last_page < self.release_pages_to_handle else self.release_pages_to_handle
        for page in range(2, finish + 1):
            url = self.git_release_pager.format(release_details[0], page)
            response = requests.get(url, headers=self.header)
            if response.status_code != 200:
                logging.warning(f"Collect GH data response: {response.status_code}")
                break
            resp = response.json()
            result += self.collect_gh_releases(resp)
        return result

    @staticmethod
    def extract_release_details(response) -> tuple:
        tracker_number = ''
        last_page_number = 0
        if 'link' in response.headers:
            # why don't they introduced 3 headers instead of this bullshit?
            links = response.headers['link']
            last_page = str(links).split(',')[1].split(";")[0].split("/")
            last_page_number = int(last_page[len(last_page) - 1].split("=")[1][:-1])
            tracker_number = last_page[4]
            logging.info(f"Number of release pages are {last_page_number}")
        return tracker_number, last_page_number

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
