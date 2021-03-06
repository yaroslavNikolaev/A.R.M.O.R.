from utils.collectors import MavenCentralVersionCollector
from utils.configuration import Configuration


class SpannerCollector(MavenCentralVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "spanner"

    group_id = "com.google.cloud"
    artifact_id = "google-cloud-spanner"

    def __init__(self, config: Configuration):
        super().__init__(config, self.group_id, self.artifact_id)


class BigTableCollector(MavenCentralVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "bigtable"

    group_id = "com.google.cloud.bigtable"
    artifact_id = "bigtable-hbase-2.x"

    def __init__(self, config: Configuration):
        super().__init__(config, self.group_id, self.artifact_id)
