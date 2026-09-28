# Platform images

Container image definitions and Helm charts for platform services. Each image lives in its own directory under `images/`; reusable Kubernetes packaging lives under `charts/`.

## Repository layout

```text
images/<name>/       Image definition, manifest, pinned dependencies, docs, and tests
charts/<name>/       Helm chart for deploying the corresponding image
scripts/              Manifest validation and repository-level helpers
.github/workflows/   Generic build, scan, attest, and publish workflows
```

## Images

### OpenBB Platform

The curated OpenBB image is defined in [`images/openbb/`](images/openbb/). It is a non-root `linux/amd64` API image with OpenBB metadata generated during the image build. See the [OpenBB image README](images/openbb/README.md) for its upstream source, licenses, update procedure, and digest-based deployment instructions.

Each image directory must contain an `image.json` manifest. The generic workflow discovers `images/*/image.json`, validates its paths and platforms, builds a validation matrix, runs the image-specific smoke test, lints its chart when present, scans the image, and publishes from the approved release path. Adding an image therefore means adding one manifest and following the same directory contract; no workflow edit is required.

Build and run it locally from the repository root:

```sh
docker build --file images/openbb/Dockerfile --tag platform-images/openbb:local .
images/openbb/tests/smoke.sh platform-images/openbb:local
```

To run the API interactively instead, use `docker run --rm --publish 6900:6900 platform-images/openbb:local`.

The API documentation is available at <http://127.0.0.1:6900/docs>.

## Helm

The OpenBB chart supports either a normal tag for development or an immutable image digest for deployments:

```sh
helm upgrade --install openbb ./charts/openbb \
  --set image.repository=ghcr.io/buildorbit/platform-images/openbb \
  --set image.digest=sha256:<published-digest>
```

Do not commit secrets, provider API keys, private infrastructure details, or deployment-specific configuration to this repository.

## Image releases

The workflow publishes immutable SHA references for every build. It also publishes semantic tags for GitHub Releases: publishing a release with tag `v0.1.0` produces `0.1.0`, `0.1`, and `0` tags for each image. The `latest` tag is reserved for successful builds from `main`.

The semantic image version is independent of the upstream application version. For example, the OpenBB package version remains documented in [`images/openbb/README.md`](images/openbb/README.md), while the curated image can release as `0.1.0`, `0.1.1`, and so on.

Images with a matching Helm chart also publish an OCI chart from the same GitHub Release. A release tagged `v0.1.0` publishes `oci://ghcr.io/buildorbit/platform-images/charts/openbb` at chart version `0.1.0`:

```sh
helm upgrade --install openbb oci://ghcr.io/buildorbit/platform-images/charts/openbb \
  --version 0.1.0 \
  --set image.repository=ghcr.io/buildorbit/platform-images/openbb \
  --set image.digest=sha256:<published-digest>
```

The chart version comes from the release tag; the chart's `appVersion` continues to describe the upstream application version.
