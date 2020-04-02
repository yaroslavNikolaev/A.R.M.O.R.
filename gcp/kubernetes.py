from http.client import HTTPSConnection
from utils.versions import ApplicationVersion
from utils.collectors import VersionCollector
from utils.configuration import Configuration
import typing
import json
import logging


class K8GCP(VersionCollector):
    @staticmethod
    def get_application_name() -> str:
        return "gke"

    gcp = "container.googleapis.com"
    # todo raise request to gcp to provide API without auth and link to existing env, only current version
    template = "/v1/projects/{}/zones/{}/serverconfig"
    available_updates: str
    stable_versions = '^v\d+\.\d+\.\d+$'
    auth: map

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.available_updates = self.template.format(config.gcp_project(), config.gcp_zone())
        self.auth = {"Authorization": "Bearer " + config.gcp_token(), "Content-type": "application/json"}

    def collect(self) -> typing.List[ApplicationVersion]:
        connection = HTTPSConnection(host=self.gcp)
        connection.request(url=self.available_updates, method="GET", headers=self.auth)
        response = connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        if 'error' in resp:
            logging.warning(f"Error during fetching of GKE versions: {resp.error}")
            raise LookupError(resp.error)
        releases = resp['validMasterVersions']
        result = []
        for release in releases:
            release_version = ApplicationVersion("kubernetes", release, "node", "master")
            result += [release_version]

        releases = resp['validNodeVersions']
        for release in releases:
            release_version = ApplicationVersion("kubernetes", release, "node", "nodes")
            result += [release_version]
        return result
