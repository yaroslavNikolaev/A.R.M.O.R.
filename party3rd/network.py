from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration


class NginxVersionCollector(GitHubVersionCollector):
    owner = "nginx"
    repo = "nginx"

    @staticmethod
    def get_application_name() -> str:
        return "nginx"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class CalicoVersionCollector(GitHubVersionCollector):
    owner = "projectcalico"
    repo = "calico"

    @staticmethod
    def get_application_name() -> str:
        return "calico"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class HaproxyVersionCollector(GitHubVersionCollector):
    owner = "haproxy"
    repo = "haproxy"

    @staticmethod
    def get_application_name() -> str:
        return "haproxy"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)