Ali FTOUNI et Christian MOUAWAD

# Générateur de profils Container + Kubernetes

Ce projet permet de générer automatiquement :
- une recette de build Docker à partir d’un **profil** (OS de base + paquets)
- des manifestes Kubernetes (Namespace, Deployment, Service)
- des **NetworkPolicies Kubernetes** (couches L3/L4) à partir du profil

## Structure du dépôt
- `profiles/` : profils d’entrée (YAML/JSON)
- `builder/`  : code du générateur (parsing, génération du Dockerfile et des manifestes)
- `k8s/`      : templates Kubernetes ou sorties générées (selon l’organisation choisie)
- `scripts/`  : scripts utilitaires (build, push, déploiement)
- `docs/`     : documentation (spécification des profils, notes de conception)

## Démarrage rapide (prévu)
1) Placer un profil dans `profiles/`
2) Lancer le générateur pour produire :
   - un Dockerfile
   - des fichiers YAML Kubernetes (Namespace / Deployment / Service / NetworkPolicy)
3) Construire et taguer l’image Docker
4) Pousser l’image vers un registre public
5) Déployer sur un cluster Kubernetes avec une seule commande

> Remarque : les commandes exactes seront ajoutées au fur et à mesure de l’implémentation du générateur.

## Exemple implémenté : Telegraf Alpine

Profil : `profiles/telegraf-alpine.yaml`

### Contraintes respectées
- OS : Alpine 3.19
- Package : telegraf
- Ingress : interdit (default deny)
- Egress : autorisé uniquement en TCP/443 vers un endpoint de monitoring

### Génération
```bash
python3 builder/main.py profiles/telegraf-alpine.yaml



