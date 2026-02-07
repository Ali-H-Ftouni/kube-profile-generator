# Spécification des profils (Profile) — v1

Un profil décrit :
1) l’image de base (OS/distro) pour construire un conteneur
2) la liste des packages/outils à installer
3) les règles réseau (Kubernetes NetworkPolicy) en L3/L4 uniquement

## Format
- Fichier YAML (ou JSON équivalent)
- Champs obligatoires : `apiVersion`, `kind`, `metadata.name`, `spec.image`, `spec.packages`, `spec.networkPolicy`

## Champs

### apiVersion
Valeur : `profilegen.dev/v1`

### kind
Valeur : `Profile`

### metadata.name
Identifiant du profil (utilisé pour les dossiers `dist/`, tags d’image, etc.)
Ex: `telegraf-alpine`

### spec.image
Décrit l’image de base.
- `base` (string) : ex `alpine`, `debian`, `ubuntu`
- `tag` (string) : ex `"3.19"`, `"12"`, `"22.04"`

L’image Docker finale sera typiquement : `${base}:${tag}`.

### spec.packages
Liste des packages/outils à installer dans le conteneur.
Type : liste de strings.
Ex: `["telegraf", "curl"]`

### spec.networkPolicy
Décrit la NetworkPolicy à générer.

#### podSelectorLabels
Labels appliqués aux pods (doivent matcher le Deployment).
Type : map clé/valeur.
Ex: `{ app: telegraf }`

#### policyTypes
Liste : `["Ingress", "Egress"]` (une ou deux valeurs)

#### defaultDeny
- `ingress` (bool)
- `egress` (bool)

Si `true`, une règle "deny by default" sera générée (via une NetworkPolicy sans règles permissives).

#### ingress / egress
Liste d’exceptions.
Chaque entrée contient :
- `name` (string)
- `from` (pour ingress) / `to` (pour egress) : liste de destinations/sources, supportant :
  - `namespaceSelector.matchLabels`
  - `podSelector.matchLabels`
  - `ipBlock.cidr` (et optionnellement `ipBlock.except`)
- `ports` : liste de ports L4
  - `protocol`: `TCP` ou `UDP`
  - `port`: entier (1-65535)

## Contraintes
- L3/L4 seulement : pas de règles HTTP, pas de FQDN.
- Un port doit être un entier.
- Si `ingress` est vide et `defaultDeny.ingress=true` => aucun trafic entrant autorisé.
- Si `egress` est vide et `defaultDeny.egress=true` => aucun trafic sortant autorisé.

## Exemple
Voir `profiles/example-telegraf-alpine.yaml`.
