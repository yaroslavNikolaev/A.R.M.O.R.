from copy import copy


def _extract_numbers(version: str) -> int:
    result = ""
    for char in version:
        if char.isdigit():
            result += char
    return int(result)


class NodeVersion(object):
    major: int
    minor: int
    release: int
    built: int
    node_name: str
    pod_name: str
    app: str

    def __init__(self, app: str, version: str, node: str = "-", pod: str = "-"):
        versions = version.split(".")
        self.major = _extract_numbers(versions[0])
        self.minor = _extract_numbers(versions[1])
        self.release = _extract_numbers(versions[2])
        self.built = _extract_numbers(versions[3]) if len(versions) > 3 else 0
        self.node_name = node
        self.pod_name = pod
        self.app = app

    def __sub__(self, other):
        result = copy(ZERO_VERSION)
        result.major = self.major - other.major
        result.minor = self.minor - other.minor
        result.release = self.release - other.release
        result.built = self.built - other.built
        return result


ZERO_VERSION = NodeVersion("", "v0.0.0")
