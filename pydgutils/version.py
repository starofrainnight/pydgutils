from collections import namedtuple

# Release levels
RL_ALPHA = 'alpha'
RL_BETA = 'beta'
RL_CANDIDATE = 'candidate'
RL_FINAL = 'final'

def version_info_to_str(version_info):
    return ".".join([str(a) for a in version_info[:3]])

def read_version_file(base_dir, package_name):
    import os.path

    package_name = package_name.replace("-", "_").replace(".", "/")
    version_file_path = os.path.join(base_dir, package_name, "version.py")
    with open(version_file_path) as f:
        return f.read()

# Version info structure just like python3's sys.version_info
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(0, 0, 10, RL_ALPHA, 0)
__version__ = version_info_to_str(version_info)
