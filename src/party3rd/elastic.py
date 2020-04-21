from utils.collectors import GitHubVersionCollector
from utils.configuration import Configuration
from abc import ABC

owner = "elastic"


class BeatsVersionCollector(GitHubVersionCollector, ABC):
    repo = "beats"

    def __init__(self, config: Configuration):
        super().__init__(config, owner, self.repo)


class FilebeatCollector(BeatsVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "filebeat"


class MetricbeatCollector(BeatsVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "metricbeat"


class AuditbeatCollector(BeatsVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "auditbeat"


class JournalbeatCollector(BeatsVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "journalbeat"


class KibanaVersionCollector(GitHubVersionCollector):
    repo = "kibana"

    @staticmethod
    def get_application_name() -> str:
        return "kibana"

    def __init__(self, config: Configuration):
        super().__init__(config, owner, self.repo)


class ElasticsearchVersionCollector(GitHubVersionCollector):
    repo = "elasticsearch"

    @staticmethod
    def get_application_name() -> str:
        return "elasticsearch"

    def __init__(self, config: Configuration):
        super().__init__(config, owner, self.repo)


class LogstashVersionCollector(GitHubVersionCollector):
    repo = "logstash"

    @staticmethod
    def get_application_name() -> str:
        return "logstash"

    def __init__(self, config: Configuration):
        super().__init__(config, owner, self.repo)
