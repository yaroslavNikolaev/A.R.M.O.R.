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

    def __init__(self, version: str):
        versions = version.split(".")
        self.major = _extract_numbers(versions[0])
        self.minor = _extract_numbers(versions[1])
        self.release = _extract_numbers(versions[2].split("-")[0])

    def __sub__(self, other):
        major = self.major - other.major
        minor = self.minor - other.minor if major == 0 else 0
        release = self.release - other.release if minor == 0 else self.release
        return Version("v" + major + "." + minor + "." + release)

    def get_float_value(self):
        return self.major * 100 + self.minor + self.release / 100


class NodeVersion(Version):
    node_name: str

    def __init__(self, version: str, node: str):
        super().__init__(version)
        self.node_name = node

    def __sub__(self, other):
        major = self.major - other.major
        minor = self.minor - other.minor if major == 0 else 0
        release = self.release - other.release if minor == 0 else self.release
        return NodeVersion("v" + str(major) + "." + str(minor) + "." + str(release), other.node_name)
