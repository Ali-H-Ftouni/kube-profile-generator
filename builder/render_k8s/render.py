import os
import yaml

def _service_ports_from_profile(profile: dict):
    """
    Try to derive Service ports from networkPolicy ingress ports.
    If none found, default to TCP/80.
    """
    np = profile["spec"].get("networkPolicy", {})
    ingress = np.get("ingress", []) or []

    ports = []
    seen = set()
    for rule in ingress:
        for p in rule.get("ports", []) or []:
            proto = str(p.get("protocol", "TCP")).upper()
            port = int(p.get("port", 80))
            key = (proto, port)
            if key in seen:
                continue
            seen.add(key)
            ports.append({
                "name": f"{proto.lower()}-{port}",
                "protocol": proto,
                "port": port,
                "targetPort": port,
            })

    if not ports:
        ports = [{
            "name": "tcp-80",
            "protocol": "TCP",
            "port": 80,
            "targetPort": 80,
        }]

    return ports

def render_manifests(profile: dict, out_dir: str, image_ref: str | None = None):
    profile_id = profile["metadata"]["name"]

    labels = profile["spec"]["networkPolicy"].get("podSelectorLabels", {"app": profile_id})
    namespace_name = f"ns-{profile_id}"

    # Image: prefer explicit image_ref, otherwise build from base:tag (ok for local/kind/minikube)
    if image_ref is None:
        base = profile["spec"]["image"]["base"]
        tag = profile["spec"]["image"]["tag"]
        image_ref = f"{base}:{tag}"

    # --- Namespace
    ns = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": namespace_name},
    }

    # --- Deployment
    container_ports = [{"containerPort": p["targetPort"], "protocol": p["protocol"]} for p in _service_ports_from_profile(profile)]
    deploy = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": profile_id,
            "namespace": namespace_name,
            "labels": labels,
        },
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": labels},
            "template": {
                "metadata": {"labels": labels},
                "spec": {
                    "containers": [{
                        "name": profile_id,
                        "image": image_ref,
                        "imagePullPolicy": "IfNotPresent",
                        "ports": container_ports,
                    }]
                },
            },
        },
    }

    # --- Service (ClusterIP)
    svc = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": profile_id,
            "namespace": namespace_name,
            "labels": labels,
        },
        "spec": {
            "type": "ClusterIP",
            "selector": labels,
            "ports": _service_ports_from_profile(profile),
        },
    }

    # Write files
    manifests_dir = os.path.join(out_dir, "manifests")
    os.makedirs(manifests_dir, exist_ok=True)

    def write(name: str, obj: dict):
        path = os.path.join(manifests_dir, name)
        with open(path, "w") as f:
            yaml.safe_dump(obj, f, sort_keys=False)
        return path

    paths = [
        write("00-namespace.yaml", ns),
        write("10-deployment.yaml", deploy),
        write("20-service.yaml", svc),
    ]
    return paths
