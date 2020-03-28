from utils.collectors import MavenCentralVersionCollector, singleton
from utils.configuration import Configuration


@singleton
class SpannerCollector(MavenCentralVersionCollector):

    @staticmethod
    def get_application_name() -> str:
        return "spanner"

    group_id = "com.google.cloud"
    artifact_id = "google-cloud-spanner"

    def __init__(self, config: Configuration):
        super().__init__(config, self.group_id, self.artifact_id)
