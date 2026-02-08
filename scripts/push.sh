#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   DOCKERHUB_USER=<your_dockerhub_username> ./scripts/push.sh profiles/example-telegraf-alpine.yaml

PROFILE_FILE="${1:-}"

if [[ -z "$PROFILE_FILE" || ! -f "$PROFILE_FILE" ]]; then
  echo "Usage: DOCKERHUB_USER=<user> ./scripts/push.sh <profile.yaml>"
  exit 1
fi

: "${DOCKERHUB_USER:?Set DOCKERHUB_USER env var}"

PY_OUT="$(python3 - <<PY
from builder.parse_profile import parse_profile
p = parse_profile("$PROFILE_FILE")
print(p["metadata"]["name"])
print(p["spec"]["image"]["base"])
print(p["spec"]["image"]["tag"])
PY
)"

PROFILE_ID="$(echo "$PY_OUT" | sed -n '1p')"
OS_BASE="$(echo "$PY_OUT" | sed -n '2p')"
OS_TAG="$(echo "$PY_OUT" | sed -n '3p')"

GITSHA="$(git rev-parse --short HEAD 2>/dev/null || echo nogit)"
PROFILEHASH="$(sha256sum "$PROFILE_FILE" | awk '{print $1}' | cut -c1-8)"

FINAL_TAG="${OS_BASE}-${OS_TAG}-${GITSHA}-${PROFILEHASH}"

LOCAL_IMAGE="${PROFILE_ID}:latest"

if ! docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then
  echo "Local image not found: $LOCAL_IMAGE"
  echo "Build it first (STEP 4), e.g.: docker build -t ${LOCAL_IMAGE} dist/${PROFILE_ID}"
  exit 1
fi

REMOTE_IMAGE="docker.io/${DOCKERHUB_USER}/${PROFILE_ID}:${FINAL_TAG}"

echo "Tagging: $LOCAL_IMAGE -> $REMOTE_IMAGE"
docker tag "$LOCAL_IMAGE" "$REMOTE_IMAGE"

echo "Pushing: $REMOTE_IMAGE"
docker push "$REMOTE_IMAGE"

echo "✅ Pushed: $REMOTE_IMAGE"
