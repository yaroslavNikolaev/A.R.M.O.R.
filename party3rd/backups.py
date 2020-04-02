from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration


class VeleroVersionCollector(GitHubVersionCollector):
    owner = "vmware-tanzu"
    repo = "velero"

    @staticmethod
    def get_application_name() -> str:
        return "velero"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)
