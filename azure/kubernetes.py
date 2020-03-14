from http.client import HTTPSConnection
from utils.versions import NodeVersion
import re
import typing
import json


class K8Azure(object):
    azure = "management.azure.com"
    # todo raise request to azure to provide API without auth and link to existing env, only current version 
    template = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.ContainerService/managedClusters/{}/upgradeProfiles/default?api-version=2020-02-01"
    available_updates: str
    stable_versions = '^v\d+\.\d+\.\d+$'
    auth: map

    def __init__(self, args):
        self.available_updates = self.template.format(args.azureSubscription, args.azureResourceGroup, args.aks)
        self.auth = {"Authorization": "Bearer " + args.azuretoken, "Content-type": "application/json"}
        pass

    def collect(self) -> typing.List[NodeVersion]:
        connection = HTTPSConnection(host=self.azure)
        connection.request(url=self.available_updates, method="GET", headers=self.auth)
        response = connection.getresponse()
        resp = json.loads(response.read().decode("utf-8"))
        releases = resp['properties']['controlPlaneProfile']['upgrades']
        result = []
        for release in releases:
            release_version = NodeVersion(release['kubernetesVersion'], "preview")
            result += [release_version]
            break

        return result
