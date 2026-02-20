Ali Ftouni et Christian Mouawad

Démarrage rapide – Lancer le programme complet

Ce projet permet de générer automatiquement une image OCI, un déploiement Kubernetes et des NetworkPolicies à partir d’un seul profil.
Les étapes ci-dessous décrivent comment exécuter l’ensemble du pipeline, depuis le clonage du dépôt jusqu’au déploiement sur Kubernetes.

1. Cloner le dépôt

Commencez par cloner le dépôt GitHub et vous placer dans le dossier du projet :

git clone https://github.com/Ali-H-Ftouni/kube-profile-generator.git
cd kube-profile-generator

2. Préparer l’environnement

Avant d’exécuter le programme, assurez-vous que :

Docker est installé et en cours d’exécution

kubectl est installé

Vous avez accès à un cluster Kubernetes
(Minikube, kind ou cluster distant)

Vous disposez d’un compte Docker Hub (repository public)

Vérification rapide :

docker ps
kubectl cluster-info

3. Choisir un profil

Les profils sont stockés dans le dossier profiles/.
Chaque profil décrit :

l’OS de base,

les logiciels à installer,

les règles réseau (ingress / egress).

Exemple utilisé dans le projet :

profiles/example-telegraf-alpine.yaml

4. Construire l’image OCI

Cette étape :

lit le profil,

génère dynamiquement un Dockerfile,

construit l’image conteneur localement.

bash scripts/build.sh profiles/example-telegraf-alpine.yaml

Les fichiers générés sont placés automatiquement dans le dossier dist/ (créé localement).

5. Pousser l’image vers Docker Hub

Connexion (si nécessaire) :

docker login

Puis pousser l’image :

bash scripts/push.sh profiles/example-telegraf-alpine.yaml

6. Déployer sur Kubernetes

Cette étape :

génère les manifests Kubernetes (Namespace, Deployment, Service),

génère les NetworkPolicies (default deny + exceptions),

applique toutes les ressources sur le cluster.

bash scripts/deploy.sh profiles/example-telegraf-alpine.yaml

7. Vérifier le déploiement
kubectl get pods -n telegraf-alpine
kubectl get svc -n telegraf-alpine
kubectl get netpol -n telegraf-alpine

Résultat attendu :

le pod est en état Running

les NetworkPolicies sont appliquées

le trafic ingress est bloqué

le trafic egress est autorisé uniquement selon le profil
(ex. TCP/443 pour Telegraf)

N.B. Note importante sur le dossier dist/

Le dossier dist/ contient uniquement des fichiers générés automatiquement.
Il n’est pas versionné sur GitHub, car il peut être recréé à tout moment en exécutant les scripts ci-dessus.
