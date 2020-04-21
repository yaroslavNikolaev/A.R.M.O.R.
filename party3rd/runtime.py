from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration
from utils.versions import ApplicationVersion, _extract_numbers


class OpenJdkVersionCollector(GitHubVersionCollector):
    owner = "openjdk"
    repo = "jdk"

    @staticmethod
    def get_application_name() -> str:
        return "openjdk"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)
        self.release_pages_to_handle = 15

    def release_to_version(self, release: str) -> ApplicationVersion:
        app = self.get_application_name()
        # 'jdk-15+19' -> "v1.15.0-19"
        versions = release.split("+")
        converted_release = "v1." + str(_extract_numbers(versions[0])) + ".0-" + str(_extract_numbers(versions[1]))
        return ApplicationVersion(app, converted_release)
