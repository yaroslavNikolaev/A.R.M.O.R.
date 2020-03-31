from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration


class AclVersionCollector(GitHubVersionCollector):
    owner = "acl-dev"
    repo = "acl"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)

    @staticmethod
    def get_application_name() -> str:
        return "acl"
