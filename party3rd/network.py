from utils.collectors import GitHubVersionCollector, singleton
from utils.configuration import Configuration


@singleton
class NginxVersionCollector(GitHubVersionCollector):
    owner = "nginx"
    repo = "nginx"

    @staticmethod
    def get_application_name() -> str:
        return "nginx"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)
