from enum import Enum
from utils.versions import Channel
from abc import ABC, abstractmethod
import typing


class Severity(Enum):
    NONE = "none"
    NEGLIGIBLE = "negligible"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class AbstractSeverityVerifier(ABC):

    @abstractmethod
    def get_severity(self, channel: Channel, value: int) -> Severity:
        pass

    @staticmethod
    @abstractmethod
    def get_application_name() -> str:
        pass


class MapSeverityVerifier(AbstractSeverityVerifier, ABC):
    map: typing.Dict[Channel, typing.Dict[Severity, int]]

    def __init__(self):
        self.map = {
            Channel.MINOR: self.get_minor_severity_map(),
            Channel.MAJOR: self.get_major_severity_map(),
            Channel.RELEASE: self.get_release_severity_map(),
            Channel.BUILD: self.get_build_severity_map(),
        }

    def get_severity(self, channel: Channel, value: int) -> Severity:
        severities = self.map[channel]
        result = Severity.NONE
        for severity in SEVERITIES:
            if severity in severities and value >= severities[severity]:
                result = severity
                break
        return result

    @abstractmethod
    def get_minor_severity_map(self) -> typing.Dict[Severity, int]:
        pass

    @abstractmethod
    def get_major_severity_map(self) -> typing.Dict[Severity, int]:
        pass

    @abstractmethod
    def get_release_severity_map(self) -> typing.Dict[Severity, int]:
        pass

    @abstractmethod
    def get_build_severity_map(self) -> typing.Dict[Severity, int]:
        pass


class DefaultMapSeverityVerifier(MapSeverityVerifier):
    major = {
        Severity.MAJOR: 1,
        Severity.CRITICAL: 2,
    }
    minor = {
        Severity.MODERATE: 1,
        Severity.MAJOR: 2,
        Severity.CRITICAL: 4,
    }
    release = {
        Severity.NEGLIGIBLE: 1,
        Severity.MODERATE: 2,
        Severity.MAJOR: 4,
        Severity.CRITICAL: 8,
    }

    build = {
        Severity.NEGLIGIBLE: 2,
        Severity.MODERATE: 4,
        Severity.MAJOR: 8,
        Severity.CRITICAL: 16,
    }

    def get_minor_severity_map(self) -> typing.Dict[Severity, int]:
        return self.minor

    def get_major_severity_map(self) -> typing.Dict[Severity, int]:
        return self.major

    def get_release_severity_map(self) -> typing.Dict[Severity, int]:
        return self.release

    def get_build_severity_map(self) -> typing.Dict[Severity, int]:
        return self.build

    @staticmethod
    def get_application_name() -> str:
        return "default"


SEVERITIES = [Severity.CRITICAL, Severity.MAJOR, Severity.MODERATE, Severity.NEGLIGIBLE]
