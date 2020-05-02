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

    def set_channel_version(self, channel: Channel, value: int):
        if channel == Channel.BUILD:
            self.build = value
        elif channel == Channel.RELEASE:
            self.release = value
        elif channel == Channel.MINOR:
            self.minor = value
        elif channel == Channel.MAJOR:
            self.major = value

    def __str__(self):
        return "v." + str(self.major) + "." + str(self.minor) + "." + str(self.release) + "-" + str(self.build)

    def short_app_name(self):
        return self.app.split(".")[-1]

    def resource_definition(self):
        return self.resource + " : " + self.resource_name

    def get_first_positive_valid_channel(self):
        result = None
        for channel in CHANNELS:
            value = self.get_channel_version(channel)
            if value == 0:
                continue

            if value > 0:
                result = channel
            break
        return result

    def __eq__(self, other):
        result = True
        for channel in CHANNELS:
            result = result and self.get_channel_version(channel) == other.get_channel_version(channel)
        return result

    def __ne__(self, other):
        return not self.__eq__(other)


CHANNELS = [Channel.MAJOR, Channel.MINOR, Channel.RELEASE, Channel.BUILD]
ZERO_VERSION = ApplicationVersion("", "v0.0.0")
