import os
import yaml

def _k8s_ports(port_list):
    out = []
    for p in port_list or []:
        proto = str(p.get("protocol", "TCP")).upper()
        port = int(p.get("port"))
        out.append({"protocol": proto, "port": port})
    return out

def _peer_from_item(item: dict):
    # Supporte:
    # - ipBlock: {cidr, except?}
    # - namespaceSelector: {matchLabels: {...}}  OU namespaceSelector direct {...}
    # - podSelector: {matchLabels: {...}}        OU podSelector direct {...}
    peer = {}

    if "ipBlock" in item:
        peer["ipBlock"] = item["ipBlock"]
        return peer

    if "namespaceSelector" in item:
        ns = item["namespaceSelector"]
        peer["namespaceSelector"] = ns if "matchLabels" in ns else {"matchLabels": ns}

    if "podSelector" in item:
        ps = item["podSelector"]
        peer["podSelector"] = ps if "matchLabels" in ps else {"matchLabels": ps}

    return peer

def _k8s_peers(direction_key: str, rule: dict):
    # direction_key: "from" pour ingress, "to" pour egress
    items = rule.get(direction_key, []) or []
    peers = []
    for it in items:
        peer = _peer_from_item(it)
        if peer:
            peers.append(peer)
    return peers

def render_networkpolicies(profile: dict, out_dir: str):
    profile_id = profile["metadata"]["name"]
    np = profile["spec"]["networkPolicy"]

    labels = np.get("podSelectorLabels", {"app": profile_id})
    namespace_name = f"ns-{profile_id}"

    default_deny_ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {
            "name": f"{profile_id}-default-deny-ingress",
            "namespace": namespace_name,
        },
        "spec": {
            "podSelector": {"matchLabels": labels},
            "policyTypes": ["Ingress"],
            "ingress": [],
        },
    }

    # Egress: on ne force pas par défaut, sauf si demandé ou si des règles egress existent
    default_deny_cfg = np.get("defaultDeny", {}) or {}
    has_egress_rules = bool(np.get("egress", []) or [])
    deny_egress = bool(default_deny_cfg.get("egress", False) or has_egress_rules)

    extra_policies = []

    if deny_egress:
        extra_policies.append({
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{profile_id}-default-deny-egress",
                "namespace": namespace_name,
            },
            "spec": {
                "podSelector": {"matchLabels": labels},
                "policyTypes": ["Egress"],
                "egress": [],
            },
        })

    # Exceptions policy (Ingress/Egress rules)
    ingress_rules = []
    for r in (np.get("ingress", []) or []):
        ingress_rules.append({
            "from": _k8s_peers("from", r),
            "ports": _k8s_ports(r.get("ports", [])),
        })

    egress_rules = []
    for r in (np.get("egress", []) or []):
        egress_rules.append({
            "to": _k8s_peers("to", r),
            "ports": _k8s_ports(r.get("ports", [])),
        })

    policy_types = []
    if ingress_rules:
        policy_types.append("Ingress")
    if egress_rules:
        policy_types.append("Egress")

    if policy_types:
        extra_policies.append({
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{profile_id}-allow-exceptions",
                "namespace": namespace_name,
            },
            "spec": {
                "podSelector": {"matchLabels": labels},
                "policyTypes": policy_types,
                **({"ingress": ingress_rules} if ingress_rules else {}),
                **({"egress": egress_rules} if egress_rules else {}),
            },
        })

    manifests_dir = os.path.join(out_dir, "manifests")
    os.makedirs(manifests_dir, exist_ok=True)
    out_path = os.path.join(manifests_dir, "networkpolicies.yaml")

    docs = [default_deny_ingress] + extra_policies
    with open(out_path, "w") as f:
        yaml.safe_dump_all(docs, f, sort_keys=False)

    return out_path
