from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration


class KafkaVersionCollector(GitHubVersionCollector):
    owner = "apache"
    repo = "kafka"

    @staticmethod
    def get_application_name() -> str:
        return "kafka"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)
