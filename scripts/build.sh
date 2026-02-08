
#!/bin/bash
set -e

if [ $# -ne 1 ]; then
  echo "Usage: ./scripts/build.sh <profile-name>"
  exit 1
fi

PROFILE_NAME=$1
DIST_DIR="dist/$PROFILE_NAME"
DOCKERFILE="$DIST_DIR/Dockerfile"

if [ ! -f "$DOCKERFILE" ]; then
  echo "Dockerfile not found: $DOCKERFILE"
  exit 1
fi

# Exemple simple de tagging
# profile-id:os-version
IMAGE_TAG="${PROFILE_NAME}:latest"

echo "Building Docker image: $IMAGE_TAG"
docker build -t "$IMAGE_TAG" "$DIST_DIR"

echo "Image built successfully: $IMAGE_TAG"
