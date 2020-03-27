from http.client import HTTPSConnection
from utils.versions import NodeVersion
from utils.collectors import VersionCollector
from utils.configuration import Configuration
import typing
import json


class K8Azure(VersionCollector):
    azure = "management.azure.com"
    # todo raise request to azure to provide API without auth and link to existing env, only current version 
    template = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.ContainerService/managedClusters/{}/upgradeProfiles/default?api-version=2020-02-01"
    available_updates: str
    auth: map

    def __init__(self, config: Configuration):
        self.available_updates = self.template.format(config.az_subscription(), config.az_resourceGroup(), config.aks())
        self.auth = {"Authorization": "Bearer " + config.az_token(), "Content-type": "application/json"}
        pass

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.azure)
        connection.request(url=self.available_updates, method="GET", headers=self.auth)
        response = connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        releases = resp['properties']['controlPlaneProfile']['upgrades']
        result = []
        for release in releases:
            if 'isPreview' in release and release['isPreview']:
                continue
            release_version = NodeVersion(release['kubernetesVersion'], "k8")
            result += [release_version]
            break
        return result
