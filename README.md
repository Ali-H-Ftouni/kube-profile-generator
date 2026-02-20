Démarrage rapide – Lancer le programme complet

Ce projet permet de générer automatiquement une image OCI, un déploiement Kubernetes et des NetworkPolicies à partir d’un seul profil.
Les étapes ci-dessous décrivent comment exécuter l’ensemble du pipeline, depuis le clonage du dépôt jusqu’au déploiement sur Kubernetes.

Cloner le dépôt

Commencez par cloner le dépôt GitHub et vous placer dans le dossier du projet :

git clone https://github.com/Ali-H-Ftouni/kube-profile-generator.git

cd kube-profile-generator

Préparer l’environnement

Avant d’exécuter le programme, assurez-vous que :

Docker est installé et en cours d’exécution

kubectl est installé

vous avez accès à un cluster Kubernetes (Minikube, kind ou cluster distant)

vous disposez d’un compte Docker Hub (repository public)

Vérification rapide :

docker ps
kubectl cluster-info

Choisir un profil

Les profils sont stockés dans le dossier profiles/.
Chaque profil décrit l’OS, les logiciels à installer et les règles réseau.

Exemple utilisé dans le projet :

profiles/example-telegraf-alpine.yaml

Construire l’image OCI

Cette étape :

lit le profil,

génère dynamiquement un Dockerfile,

construit l’image conteneur localement.

Commande :

bash scripts/build.sh profiles/example-telegraf-alpine.yaml

Les fichiers générés (Dockerfile, manifests, etc.) sont placés automatiquement dans le dossier dist/, qui est créé localement.

Pousser l’image vers Docker Hub

L’image construite doit être publiée sur un registry public.

Connexion (à faire une seule fois si nécessaire) :

docker login

Puis pousser l’image :

bash scripts/push.sh profiles/example-telegraf-alpine.yaml

L’image est alors disponible sur Docker Hub avec un tag incluant l’OS, l’identifiant du profil et une version ou un hash.

Déployer sur Kubernetes

Cette étape :

génère les manifests Kubernetes (Namespace, Deployment, Service),

génère les NetworkPolicies (default deny + exceptions),

applique toutes les ressources sur le cluster.

Commande :

bash scripts/deploy.sh profiles/example-telegraf-alpine.yaml

Vérifier le déploiement

Après le déploiement, vous pouvez vérifier que tout fonctionne correctement :

kubectl get pods -n telegraf-alpine
kubectl get svc -n telegraf-alpine
kubectl get netpol -n telegraf-alpine

Résultat attendu :

le pod est en état Running,

les NetworkPolicies sont présentes,

le trafic ingress est bloqué,

le trafic egress est autorisé uniquement selon les règles du profil (par exemple TCP/443 pour Telegraf).

ℹ️ Note importante sur le dossier dist/

Le dossier dist/ contient uniquement des fichiers générés automatiquement par le programme.
Il n’est pas versionné sur GitHub, car il peut être recréé à tout moment en exécutant les scripts ci-dessus.
