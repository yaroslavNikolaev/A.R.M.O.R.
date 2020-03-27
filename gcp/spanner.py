from utils.versions import MavenCentralVersionCollector


class Spanner(MavenCentralVersionCollector):
    group_id = "com.google.cloud"
    artifact_id = "google-cloud-spanner"

    def __init__(self):
        super().__init__(self.group_id, self.artifact_id)
