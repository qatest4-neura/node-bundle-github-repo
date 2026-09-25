#!/usr/bin/env bash
# Bump the node-template to a Neuraverse Node SDK release.
#
# Called by the SDK's release pipeline (neuraverse-node-sdk: release-notify-node-template) and by
# humans for a manual bump. Idempotent.
#
#   scripts/bump-sdk.sh --version 2.40.0 --wheels /path/to/wheelhouse [--release-url URL]
#
# Rewrites: SDK_VERSION; the SDK base-image tags in node-template/Dockerfile,
# node-template/docker-compose.yml, node-template-cpp/Dockerfile and .gitlab-ci.yml; the mock
# Runner image tags (:sdk-<version>) in node-template/docker-compose-mock.yml and .gitlab-ci.yml;
# node-template/wheels/ (+ SHA256SUMS) and the wheel paths in node-template/pyproject.toml;
# the version block in README.md.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"

VERSION="" WHEELS="" RELEASE_URL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --wheels) WHEELS="$2"; shift 2 ;;
    --release-url) RELEASE_URL="$2"; shift 2 ;;
    --sdk-docs|--docs-ref) shift 2 ;;   # accepted for interface parity with mock-nodegraph; docs ship via the mock docs image
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "bump-sdk: unknown argument $1" >&2; exit 2 ;;
  esac
done
[ -n "$VERSION" ] || { echo "bump-sdk: --version is required" >&2; exit 2; }
echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || { echo "bump-sdk: --version must be X.Y.Z" >&2; exit 2; }
log() { echo "bump-sdk: $*"; }

echo "$VERSION" > SDK_VERSION
log "SDK_VERSION=$VERSION"

# SDK base image (GitLab CR tags carry a v prefix, ECR tags do not; keep whichever form is there).
# .gitlab-ci.yml is in this list because scripts/check-sdk-pins.sh sweeps the whole repo for stray
# pins, so a hardcoded tag left behind here fails the check on every bump.
for f in node-template/Dockerfile node-template/docker-compose.yml node-template-cpp/Dockerfile \
         .gitlab-ci.yml; do
  [ -f "$f" ] || continue
  sed -E -i "s#(neuraverse-node-sdk:)(v?)[0-9]+\.[0-9]+\.[0-9]+#\1\2${VERSION}#g" "$f"
done
# The Mock Runner images mock-nodegraph publishes for this SDK line: its push job tags them
# sdk-<version> from its own SDK_VERSION. Pinning them is what makes a DevKit run reproducible,
# because the tag never crosses an SDK line.
for f in node-template/docker-compose.yml node-template/docker-compose-mock.yml; do
  [ -f "$f" ] || continue
  sed -E -i "s#(mock-nodegraph/(mock-backend|mock-frontend|docs):)sdk-[0-9]+\.[0-9]+\.[0-9]+#\1sdk-${VERSION}#g" "$f"
done
# bundle-devkit pulls and saves the same three images, carrying the tag once as a variable.
sed -E -i "s#(MOCK_IMAGE_TAG: )sdk-[0-9]+\.[0-9]+\.[0-9]+#\1sdk-${VERSION}#" .gitlab-ci.yml
[ "$(grep -c "sdk-${VERSION}" node-template/docker-compose-mock.yml)" -ge 3 ] \
  || { echo "bump-sdk: mock image tags in node-template/docker-compose-mock.yml not updated" >&2; exit 1; }
grep -q "MOCK_IMAGE_TAG: sdk-${VERSION}" .gitlab-ci.yml \
  || { echo "bump-sdk: MOCK_IMAGE_TAG in .gitlab-ci.yml not updated" >&2; exit 1; }
# Accept either form, exactly as scripts/check-sdk-pins.sh does since c1a1e0f.
grep -Eq "neuraverse-node-sdk:v?${VERSION}" node-template/Dockerfile \
  || { echo "bump-sdk: node-template/Dockerfile pin not updated" >&2; exit 1; }

DISTS="lib_python_neuraverse_node_sdk neuraverse_entities_apis_messages lib_python_neuraverse_common lib_python_neuraverse_service_http lib_python_neuraverse_service_grpc"
if [ -n "$WHEELS" ]; then
  [ -d "$WHEELS" ] || { echo "bump-sdk: --wheels dir not found: $WHEELS" >&2; exit 2; }
  for d in $DISTS; do
    n=$(ls "$WHEELS"/"$d"-*.whl 2>/dev/null | wc -l)
    [ "$n" -eq 1 ] || { echo "bump-sdk: expected exactly one $d-*.whl in $WHEELS, found $n" >&2; exit 1; }
  done
  ls "$WHEELS"/lib_python_neuraverse_node_sdk-"$VERSION"-*.whl >/dev/null 2>&1 || { echo "bump-sdk: SDK wheel in $WHEELS is not version $VERSION" >&2; exit 1; }
  if [ "$(cd "$WHEELS" && pwd -P)" != "$(cd node-template/wheels 2>/dev/null && pwd -P || echo none)" ]; then
    rm -f node-template/wheels/*.whl; mkdir -p node-template/wheels
    for d in $DISTS; do cp "$WHEELS"/"$d"-*.whl node-template/wheels/; done
  fi
  rm -f node-template/wheels/SHA256SUMS
  ( cd node-template/wheels && sha256sum ./*.whl | sed 's#\./##' | LC_ALL=C sort -k2 > SHA256SUMS )
  for d in $DISTS; do
    whl=$(basename "$(ls node-template/wheels/"$d"-*.whl)")
    grep -Eq "path = \"wheels/${d}-[^\"]+\"" node-template/pyproject.toml || { echo "bump-sdk: pyproject has no wheel path for ${d}" >&2; exit 1; }
    sed -E -i "s#path = \"wheels/${d}-[^\"]+\"#path = \"wheels/${whl}\"#" node-template/pyproject.toml
    [ "$(grep -c "wheels/${whl}\"" node-template/pyproject.toml)" -eq 1 ] || { echo "bump-sdk: ${whl} must appear exactly once in pyproject.toml" >&2; exit 1; }
  done
  log "wheels replaced: $(ls node-template/wheels/*.whl | xargs -n1 basename | tr '\n' ' ')"
fi

# README version block
if [ -f README.md ] && grep -q '<!-- BEGIN sdk-version -->' README.md; then
  rel="${RELEASE_URL:-https://gitlab.neura-robotics.com/neuraverse/neuraverse-node-sdk/-/releases/v${VERSION}}"
  awk -v v="$VERSION" -v rel="$rel" '
    /<!-- BEGIN sdk-version -->/ { print; print "Bundled Neuraverse Node SDK: **v" v "** ([release notes](" rel ")). Mock Runner images: tag `sdk-" v "`."; skip=1; next }
    /<!-- END sdk-version -->/ { skip=0 }
    !skip { print }
  ' README.md > README.md.tmp && mv README.md.tmp README.md
  log "README version block updated"
fi
log "done. Run scripts/check-sdk-pins.sh to verify."
