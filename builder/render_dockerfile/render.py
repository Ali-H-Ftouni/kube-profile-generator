import os

def render_dockerfile(profile: dict, output_dir: str):
    image = profile["spec"]["image"]
    packages = profile["spec"]["packages"]

    base = image["base"]
    tag = image["tag"]
    image_name = f"{base}:{tag}"

    lines = []
    lines.append(f"FROM {image_name}")

    if base == "alpine":
        pkg_line = " ".join(packages)
        lines.append(f"RUN apk add --no-cache {pkg_line}")
        lines.append('CMD ["sh"]')

    elif base in ["debian", "ubuntu"]:
        pkg_line = " ".join(packages)
        lines.append(
            "RUN apt-get update && apt-get install -y "
            + pkg_line
            + " && rm -rf /var/lib/apt/lists/*"
        )
        lines.append('CMD ["bash"]')

    else:
        raise ValueError(f"Unsupported base image: {base}")

    os.makedirs(output_dir, exist_ok=True)

    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write("\n".join(lines))

    return dockerfile_path

