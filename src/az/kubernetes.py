from utils.versions import ApplicationVersion
from utils.collectors import VersionCollector
from utils.configuration import Configuration
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.containerservice import ContainerServiceClient
import typing


class K8Azure(VersionCollector):
    # todo raise request to az to provide API without auth and link to existing env, only current version
    client: ContainerServiceClient
    rg: str
    aks: str

    def __init__(self, config: Configuration):
        super().__init__(config)
        credentials = ServicePrincipalCredentials(config.az_client(), config.secret(), tenant=config.az_tenant())
        self.client = ContainerServiceClient(credentials, config.az_subscription())
        self.rg = config.az_resource_group()
        self.aks = config.aks()

    def collect(self) -> typing.List[ApplicationVersion]:
        result = []
        res = self.client.managed_clusters.get_upgrade_profile(self.rg, self.aks)
        for release in res.control_plane_profile.upgrades:
            release_version = ApplicationVersion("kubernetes", release.kubernetes_version, "node", "k8")
            result += [release_version]
            break
        return result

    @staticmethod
    def get_application_name() -> str:
        return "aks"
