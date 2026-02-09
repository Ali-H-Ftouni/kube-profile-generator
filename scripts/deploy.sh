#!/usr/bin/env bash
set -e

PROFILE_ID="$1"

if [ -z "$PROFILE_ID" ]; then
  echo "Usage: $0 <profile-id>"
  echo "Example: $0 telegraf-alpine"
  exit 1
fi

MANIFEST_DIR="dist/${PROFILE_ID}/manifests"

if [ ! -d "$MANIFEST_DIR" ]; then
  echo "Manifests directory not found: $MANIFEST_DIR"
  exit 1
fi

echo "Deploying profile: ${PROFILE_ID}"
echo "Applying manifests from: ${MANIFEST_DIR}"

kubectl apply -f "${MANIFEST_DIR}"

echo "Deployment completed for profile: ${PROFILE_ID}"
