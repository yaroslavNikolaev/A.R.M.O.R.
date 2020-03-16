from http.client import HTTPSConnection
from utils.versions import NodeVersion
from utils.versions import VersionCollector
import typing
import json


class K8GCP(VersionCollector):
    azure = "container.googleapis.com"
    # todo raise request to gcp to provide API without auth and link to existing env, only current version
    template = "/v1/projects/{}/zones/{}/serverconfig"
    available_updates: str
    stable_versions = '^v\d+\.\d+\.\d+$'
    auth: map

    def __init__(self, args):
        self.available_updates = self.template.format(args.gcpproject, args.gcpzone)
        self.auth = {"Authorization": "Bearer " + args.gcptoken, "Content-type": "application/json"}
        pass

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.azure)
        connection.request(url=self.available_updates, method="GET", headers=self.auth)
        response = connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        releases = resp['validMasterVersions']
        result = []
        for release in releases:
            release_version = NodeVersion(release, "master")
            result += [release_version]

        releases = resp['validNodeVersions']
        for release in releases:
            release_version = NodeVersion(release, "nodes")
            result += [release_version]
        return result
