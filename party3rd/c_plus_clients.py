from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration
from abc import ABC


class AclVersionCollector(GitHubVersionCollector, ABC):
    owner = "acl-dev"
    repo = "acl"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class RedisVersionCollector(AclVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "redis"
