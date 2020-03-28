from utils.collectors import MavenCentralVersionCollector
from utils.configuration import Configuration


class SpannerCollector(MavenCentralVersionCollector):
    group_id = "com.google.cloud"
    artifact_id = "google-cloud-spanner"

    def __init__(self, config: Configuration):
        super().__init__(config, self.group_id, self.artifact_id)
