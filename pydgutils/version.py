from collections import namedtuple

# Release levels
RL_ALPHA = 'alpha'
RL_BETA = 'beta'
RL_CANDIDATE = 'candidate'
RL_FINAL = 'final'

def version_info_to_str(version_info):
    result = ".".join([str(a) for a in version_info[:3]])

    # Release level abbreviations
    # Reference to https://www.python.org/dev/peps/pep-0440/
    rl_abbreviations = {RL_ALPHA:'a', RL_BETA:'b', RL_CANDIDATE:'rc', RL_FINAL:''}
    result += rl_abbreviations[version_info.releaselevel]
    if version_info.releaselevel != RL_FINAL:
        result += str(version_info.serial)
    return result

def read_version_file(base_dir, package_name):
    import os.path

    # PEP 8: underscores is discouraged. So we won't replace "-" to "_".
    package_name = package_name.replace("-", "").replace(".", "/")
    version_file_path = os.path.join(base_dir, package_name, "version.py")
    with open(version_file_path) as f:
        return f.read()

# Version info structure just like python3's sys.version_info
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(0, 0, 12, RL_FINAL, 0)
__version__ = version_info_to_str(version_info)
