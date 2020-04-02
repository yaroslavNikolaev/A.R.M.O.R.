from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration


class GrafanaVersionCollector(GitHubVersionCollector):
    owner = "grafana"
    repo = "grafana"

    @staticmethod
    def get_application_name() -> str:
        return "grafana"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


# or network?
class KialiVersionCollector(GitHubVersionCollector):
    owner = "kiali"
    repo = "kiali"

    @staticmethod
    def get_application_name() -> str:
        return "kiali"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)


class FluentdVersionCollector(GitHubVersionCollector):
    owner = "fluent"
    repo = "fluentd"

    @staticmethod
    def get_application_name() -> str:
        return "fluentd"

    def __init__(self, config: Configuration):
        super().__init__(config, self.owner, self.repo)
