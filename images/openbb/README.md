# OpenBB Platform image

This image packages the OpenBB Platform REST API for `linux/amd64` environments that need a maintained, predictable runtime.

## Upstream and pinned versions

- Upstream project: [OpenBB Platform](https://github.com/OpenBB-finance/OpenBB)
- Python base: [official `python:3.12-slim-bookworm`](https://hub.docker.com/_/python), pinned to the multi-platform manifest digest in [`Dockerfile`](Dockerfile)
- OpenBB: `4.7.2`, pinned in [`requirements.txt`](requirements.txt)
- API launcher: `openbb-platform-api==1.3.6`, pinned in [`requirements.txt`](requirements.txt)
- API port: `6900`
- API documentation: `/docs`

OpenBB is licensed under [AGPL-3.0-only](https://github.com/OpenBB-finance/OpenBB/blob/develop/LICENSE), and the API launcher is licensed under [Apache-2.0](https://github.com/OpenBB-finance/OpenBB/blob/develop/openbb_platform_api/LICENSE). This repository does not include provider credentials or API keys.

## Runtime properties

- Runs as UID/GID `10001:10001` (`openbb`), never as root.
- Does not request Linux capabilities or privilege escalation.
- Uses `openbb-api --no-build`; `widgets.json` is generated at image build time by [`scripts/build-metadata.py`](scripts/build-metadata.py).
- The image includes a Docker health check against `http://127.0.0.1:6900/docs`.

## Local build and smoke test

Run these commands from the repository root:

```sh
docker build --file images/openbb/Dockerfile --tag platform-images/openbb:local .
images/openbb/tests/smoke.sh platform-images/openbb:local
```

The smoke test verifies that the API reaches `/docs`, runs as UID 10001, and is not configured as a privileged container.

## Updating OpenBB

1. Update both direct pins in `requirements.txt` and the corresponding Dockerfile arguments/chart `appVersion`.
2. Confirm the OpenBB release still supports the selected API launcher and Python version.
3. Build the image and run `images/openbb/tests/smoke.sh`.
4. Review the vulnerability scan and generated SBOM in the GitHub Actions run.
5. Merge through protected `main` or use the manually approved release workflow.

The dependency pins intentionally cover the two first-class OpenBB packages. The resolver installs their compatible transitive dependencies; the CI build and vulnerability scan are the reproducibility and safety gates for each published image.

## Immutable image references

The publish job records the resulting digest in the GitHub Actions summary. Inspect a tag and deploy by digest:

```sh
docker buildx imagetools inspect ghcr.io/buildorbit/platform-images/openbb:latest
docker pull ghcr.io/buildorbit/platform-images/openbb@sha256:<published-digest>
```

For Kubernetes, set the Helm chart's `image.digest` and leave `image.tag` unused. Tags are convenient aliases; the digest is the immutable deployment reference.

Semantic image tags are created from artifact-specific GitHub Releases. Publishing a release tagged `openbb-v0.1.0` publishes `0.1.0`, `0.1`, and `0` in addition to the SHA reference. `latest` is only updated by the protected `main` workflow.

## Image manifest

[`image.json`](image.json) is the contract consumed by the generic workflow:

```json
{
  "name": "openbb",
  "repository": "ghcr.io/buildorbit/platform-images/openbb",
  "context": ".",
  "dockerfile": "images/openbb/Dockerfile",
  "platforms": ["linux/amd64"],
  "validation_platform": "linux/amd64",
  "chart": "charts/openbb",
  "smoke_test": "images/openbb/tests/smoke.sh"
}
```

Paths are repository-relative. The validation platform must be one of the publish platforms, and the chart and smoke test are optional for images that do not provide them.
