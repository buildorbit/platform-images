# GitHub Actions BuildKit runner

This image is the toolchain for the opt-in `buildorbit-image-builders` ARC
scale set. It contains the GitHub Actions runner inherited from the pinned
official runner image, the Docker CLI, and a checksum-verified Buildx plugin.

It deliberately does not contain or start a Docker daemon and does not require
`/var/run/docker.sock`. Workflows use the Docker Buildx Kubernetes driver with
`rootless=true`; Buildx creates workers in the GitOps-managed `buildkit`
namespace using the runner's namespaced Kubernetes permissions.

Example workflow setup:

```sh
docker buildx create \
  --bootstrap \
  --name=buildorbit \
  --driver=kubernetes \
  --driver-opt=namespace=buildkit,rootless=true,serviceaccount=buildkit-worker \
  --use

docker buildx build \
  --builder=buildorbit \
  --platform=linux/amd64 \
  --tag ghcr.io/buildorbit/example:ci \
  --push .
```

The `buildkit-worker` ServiceAccount has no application permissions. The
runner ServiceAccount can manage only the BuildKit worker resources in the
`buildkit` namespace; it has no cluster-wide access and no permission to read
Kubernetes Secrets.

The image is released independently as
`github-actions-buildkit-runner-v<version>`. Deploy the resulting immutable
image digest in the ARC scale-set values; do not use `latest`.
