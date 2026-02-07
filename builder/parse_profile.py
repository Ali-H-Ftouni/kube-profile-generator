import yaml
import sys

class ProfileError(Exception):
    pass


def load_profile(path):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise ProfileError(f"Cannot read profile file: {e}")


def validate_profile(profile):
    # Champs racine
    for field in ["apiVersion", "kind", "metadata", "spec"]:
        if field not in profile:
            raise ProfileError(f"Missing field: {field}")

    if profile["kind"] != "Profile":
        raise ProfileError("kind must be 'Profile'")

    if "name" not in profile["metadata"]:
        raise ProfileError("metadata.name is required")

    spec = profile["spec"]

    # Image / OS
    if "image" not in spec:
        raise ProfileError("spec.image is required")
    for f in ["base", "tag"]:
        if f not in spec["image"]:
            raise ProfileError(f"spec.image.{f} is required")

    # Packages
    if "packages" not in spec or not isinstance(spec["packages"], list):
        raise ProfileError("spec.packages must be a list")

    # NetworkPolicy
    if "networkPolicy" not in spec:
        raise ProfileError("spec.networkPolicy is required")

    np = spec["networkPolicy"]
    for field in ["ingress", "egress"]:
        if field not in np:
            raise ProfileError(f"networkPolicy.{field} is required")

        for rule in np[field]:
            if "ports" not in rule:
                raise ProfileError("Each rule must define ports")


def normalize_profile(profile):
    np = profile["spec"]["networkPolicy"]

    for direction in ["ingress", "egress"]:
        for rule in np.get(direction, []):
            for p in rule.get("ports", []):
                p["protocol"] = p["protocol"].upper()
                p["port"] = int(p["port"])

    return profile


def parse_profile(path):
    profile = load_profile(path)
    validate_profile(profile)
    return normalize_profile(profile)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_profile.py <profile.yaml>")
        sys.exit(1)

    profile = parse_profile(sys.argv[1])
    print("Profile is valid")
