import typing

from utils.collectors import ConstantVersionsCollector
from utils.configuration import Configuration
from utils.versions import ApplicationVersion

postgres = "cloud-postgres"
redis = "redis-memorystore"


# https://issuetracker.google.com/154044359
class RedisMemorystoreCollector(ConstantVersionsCollector):
    application = "redis-memorystore"
    hardcoded = [
        ApplicationVersion(redis, "3.2.0"),
        ApplicationVersion(redis, "4.0.0"),
        ApplicationVersion(redis, "5.0.0")
    ]

    def __init__(self, config: Configuration, versions: typing.List[ApplicationVersion]):
        super().__init__(config, self.hardcoded)

    @staticmethod
    def get_application_name() -> str:
        return redis


# https://issuetracker.google.com/154042326
class CloudPostgresCollector(ConstantVersionsCollector):
    hardcoded = [
        ApplicationVersion(postgres, "9.6.0"),
        ApplicationVersion(postgres, "10.0.0"),
        ApplicationVersion(postgres, "11.0.0"),
        ApplicationVersion(postgres, "12.0.0"),
    ]

    def __init__(self, config: Configuration, versions: typing.List[ApplicationVersion]):
        super().__init__(config, self.hardcoded)

    @staticmethod
    def get_application_name() -> str:
        return postgres
