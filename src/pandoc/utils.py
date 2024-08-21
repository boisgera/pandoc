# Python Standard Library
import json
import warnings

# Third-Party Libraries
import importlib.resources as resources


# Pandoc-Types Version Mapping and Type Info
# ------------------------------------------------------------------------------
_json_data = resources.read_text("pandoc", "pandoc-types.json")
_data = json.loads(_json_data)
version_mapping = _data["version_mapping"]
definitions = _data["definitions"]


# Pandoc-Types Version Resolver
# ------------------------------------------------------------------------------
def version_key(string):
    return [int(s) for s in string.split(".")]


def match(spec, version):
    if len(spec) == 0 or (len(spec) >= 1 and isinstance(spec[0], list)):
        return all(match(s, version) for s in spec)
    elif spec[0] == "==":
        if "*" in spec[1]:
            vk_low = version_key(spec[1][:-2])
            vk_high = vk_low.copy()
            vk_high[-1] += 1
            return match(
                [
                    [">=", ".".join(p for p in vk_low)],
                    ["<", ".".join(p for p in vk_high)],
                ],
                version,
            )
        else:
            return spec[1] == version
    elif spec[0] == ">=":
        return version_key(version) >= version_key(spec[1])
    elif spec[0] == "<":
        return version_key(version) < version_key(spec[1])
    else:
        raise ValueError("invalid version spec {0}".format(spec))


def resolve(version, warn=True):
    pandoc_versions = sorted(version_mapping.keys(), key=version_key)
    latest_pandoc_version = pandoc_versions[-1]
    pandoc_types_versions = sorted(definitions.keys(), key=version_key)
    try:
        pandoc_types_version_spec = version_mapping[version]
    except KeyError:
        error = f"""
Pandoc version {version} is not supported, we proceed as if pandoc {latest_pandoc_version} was used. 
The behavior of the library is undefined if the document models of these versions differ."""
        warnings.warn(error)
        version = latest_pandoc_version
        pandoc_types_version_spec = version_mapping[version]

    matches = []
    for pandoc_types_version in pandoc_types_versions:
        if match(pandoc_types_version_spec, pandoc_types_version):
            matches.append(pandoc_types_version)
    return matches
