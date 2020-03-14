import abc
import typing
from prometheus_client.core import GaugeMetricFamily


class AbstractWrapper(abc.ABC):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    BARE_METAL = "metal"

    @abc.abstractmethod
    def collect(self) -> typing.List[GaugeMetricFamily]:
        pass

    def is_aws(self, environment: str) -> bool:
        return environment == self.AWS

    def is_azure(self, environment: str) -> bool:
        return environment == self.AZURE

    def is_gcp(self, environment: str) -> bool:
        return environment == self.GCP

    def is_metal(self, environment: str) -> bool:
        return environment == self.BARE_METAL


class DummyWrapper(AbstractWrapper):

    def collect(self) -> typing.List[GaugeMetricFamily]:
        return []


DUMMY_SINGLETON_WRAPPER = DummyWrapper()