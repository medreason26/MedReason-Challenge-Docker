#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-medreason-docker:latest}"
HOST_OUTPUT_DIR="${2:-$(pwd)/output}"
mkdir -p "${HOST_OUTPUT_DIR}"

# Use the lightweight smoke system for the template test.
docker run --rm \
  -e MEDREASON_SYSTEM=smoke \
  -v "$(pwd)/test:/input:ro" \
  -v "${HOST_OUTPUT_DIR}:/output" \
  "${IMAGE_NAME}"

python tools/validate_output.py "${HOST_OUTPUT_DIR}/results.json" --input-json test/cases.json

echo "Smoke test completed successfully. Output: ${HOST_OUTPUT_DIR}/results.json"
