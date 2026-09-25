#!/bin/sh
# Verify every SDK pin agrees with SDK_VERSION. POSIX sh (runs in docker:cli). Humans bump with scripts/bump-sdk.sh.
set -eu
cd "$(dirname "$0")/.."
fail() { echo "check-sdk-pins: FAIL: $*" >&2; exit 1; }
[ -f SDK_VERSION ] || fail "SDK_VERSION file missing"
V=$(tr -d '[:space:]' < SDK_VERSION)
echo "$V" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || fail "SDK_VERSION is not X.Y.Z: '$V'"

grep -Eq "neuraverse-node-sdk:v?$V" node-template/Dockerfile || fail "node-template/Dockerfile does not pin neuraverse-node-sdk:v$V or :$V"
grep -Eq "neuraverse-node-sdk:v?$V" node-template/docker-compose.yml || fail "node-template/docker-compose.yml BASE_IMAGE is not :v$V or :$V"
grep -Eq "neuraverse-node-sdk:v?$V" node-template-cpp/Dockerfile || fail "node-template-cpp/Dockerfile does not pin neuraverse-node-sdk:v$V or :$V"
for svc in mock-backend mock-frontend docs; do
  grep -q "mock-nodegraph/$svc:sdk-$V" node-template/docker-compose-mock.yml || fail "node-template/docker-compose-mock.yml: $svc image is not :sdk-$V"
done
grep -q "mock-nodegraph/[a-z-]*:latest" node-template/docker-compose-mock.yml && fail "node-template/docker-compose-mock.yml still references a mock-nodegraph :latest image"
grep -q "MOCK_IMAGE_TAG: sdk-$V" .gitlab-ci.yml || fail ".gitlab-ci.yml MOCK_IMAGE_TAG is not sdk-$V"

other=$(find . -type f \( -name '*.yml' -o -name '*.yaml' -o -name '*.md' -o -name 'Dockerfile' -o -name '*.toml' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' -o -name '*.json' \) \
  -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/wheels/*' -not -path './docs/*' \
  -exec grep -Eoh 'neuraverse-node-sdk:v?[0-9]+\.[0-9]+\.[0-9]+' {} + 2>/dev/null | grep -v ":v\{0,1\}$V\$" || true)
[ -z "$other" ] || fail "stray SDK image pins: $(echo "$other" | sort -u | tr '\n' ' ')"

[ -f node-template/wheels/lib_python_neuraverse_node_sdk-"$V"-py3-none-any.whl ] || fail "SDK wheel $V missing in node-template/wheels"
[ -f node-template/wheels/SHA256SUMS ] || fail "node-template/wheels/SHA256SUMS missing"
( cd node-template/wheels && sha256sum -c SHA256SUMS >/dev/null ) || fail "wheel checksums do not match SHA256SUMS"
for w in node-template/wheels/*.whl; do
  grep -q "wheels/$(basename "$w")\"" node-template/pyproject.toml || fail "$(basename "$w") is not referenced in node-template/pyproject.toml"
done
for p in $(grep -oE 'path = "wheels/[^"]+"' node-template/pyproject.toml | sed -E 's/path = "wheels\/([^"]+)"/\1/'); do
  [ -f "node-template/wheels/$p" ] || fail "pyproject references missing wheel $p"
done

echo "check-sdk-pins: OK (SDK $V)"
