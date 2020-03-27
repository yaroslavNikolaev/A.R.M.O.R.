from copy import copy


def _extract_numbers(version: str) -> int:
    result = ""
    for char in version:
        if char.isdigit():
            result += char
    return int(result)


class Version(object):
    major: int
    minor: int
    release: int
    built: int

    def __init__(self, version: str):
        versions = version.split(".")
        self.major = _extract_numbers(versions[0])
        self.minor = _extract_numbers(versions[1])
        self.release = _extract_numbers(versions[2])
        self.built = _extract_numbers(versions[3]) if len(versions) > 3 else 0

    def get_float_value(self):
        return self.major * 100 + self.minor + self.release / 100


class NodeVersion(Version):
    node_name: str

    def __init__(self, version: str, node: str):
        super().__init__(version)
        self.node_name = node

    def __sub__(self, other):
        result = copy(ZERO_VERSION)
        result.major = self.major - other.major
        result.minor = self.minor - other.minor
        result.release = self.release - other.release
        result.built = self.built - other.built
        return result


ZERO_VERSION = NodeVersion("v0.0.0", "")
