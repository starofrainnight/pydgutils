from collections import namedtuple

# Release levels
RL_ALPHA = 'alpha'
RL_BETA = 'beta'
RL_CANDIDATE = 'candidate'
RL_FINAL = 'final'

def version_info_to_str(version_info):
    return ".".join([str(a) for a in version_info[:3]])

# Version info structure just like python3's sys.version_info
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(0, 0, 10, RL_ALPHA, 0)
__version__ = version_info_to_str(version_info)
