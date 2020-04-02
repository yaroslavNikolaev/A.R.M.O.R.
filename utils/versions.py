from copy import copy
from enum import Enum


def _extract_numbers(version: str) -> int:
    result = ""
    for char in version:
        if char.isdigit():
            result += char
    return int(result)


class Channel(Enum):
    MAJOR = "major"
    MINOR = "minor"
    RELEASE = "release"
    BUILD = "build"


class ApplicationVersion(object):
    app: str
    major: int
    minor: int
    release: int
    build: int
    resource: str
    resource_name: str

    def __init__(self, app: str, version: str, resource: str = "-", resource_name: str = "-"):
        versions = version.split(".")
        self.major = _extract_numbers(versions[0])
        self.minor = _extract_numbers(versions[1])
        self.release = _extract_numbers(versions[2])
        self.build = _extract_numbers(versions[3]) if len(versions) > 3 else 0
        self.resource_name = resource_name
        self.resource = resource
        self.app = app

    def __sub__(self, other):
        result = copy(ZERO_VERSION)
        result.major = self.major - other.major
        result.minor = self.minor - other.minor
        result.release = self.release - other.release
        result.build = self.build - other.build
        return result

    def get_channel_version(self, channel: Channel):
        if channel == Channel.BUILD:
            return self.build
        elif channel == Channel.RELEASE:
            return self.release
        elif channel == Channel.MINOR:
            return self.minor
        elif channel == Channel.MAJOR:
            return self.major


CHANNELS = [Channel.MAJOR, Channel.MINOR, Channel.RELEASE, Channel.BUILD]
ZERO_VERSION = ApplicationVersion("", "v0.0.0")
