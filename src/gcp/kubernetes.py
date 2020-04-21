from utils.versions import ApplicationVersion
from utils.collectors import VersionCollector
from utils.configuration import Configuration
from googleapiclient import discovery
import typing
import logging


class K8GCP(VersionCollector):
    project: str
    zone: str

    @staticmethod
    def get_application_name() -> str:
        return "gke"

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.project = config.gcp_project()
        self.zone = config.gcp_zone()

    def collect(self) -> typing.List[ApplicationVersion]:
        service = discovery.build('container', 'v1')
        # todo raise request to gcp to provide API without auth and link to existing env, only current version
        server_config = service.projects().zones().getServerconfig(projectId=self.project, zone=self.zone).execute()
        if 'error' in server_config:
            logging.warning(f"Error during fetching of GKE versions: {server_config.error}")
            raise LookupError(server_config.error)
        releases = server_config['validMasterVersions']
        result = []
        for release in releases:
            release_version = ApplicationVersion("kubernetes", release, "node", "master")
            result += [release_version]

        releases = server_config['validNodeVersions']
        for release in releases:
            release_version = ApplicationVersion("kubernetes", release, "node", "nodes")
            result += [release_version]
        return result
