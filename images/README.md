# Image definition convention

Every image is a directory under `images/` with this contract:

```text
images/<name>/
  image.json       Required workflow manifest
  Dockerfile       Required container build definition
  README.md        Upstream, license, runtime, and update documentation
  tests/smoke.sh   Optional smoke test accepting one image reference
  scripts/          Optional image-build helpers
```

The matching Helm chart, when the image is deployable on Kubernetes, lives at `charts/<name>/`.

## `image.json`

The manifest uses repository-relative paths and is the source of truth for the generic GitHub Actions workflow:

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | yes | Lowercase image directory and local CI tag name |
| `version` | yes | Current semantic release version for this image and matching chart |
| `repository` | yes | Published container repository, without a tag or digest |
| `context` | yes | Docker build context |
| `dockerfile` | yes | Dockerfile path |
| `platforms` | yes | Buildx publish platforms, represented as a JSON list |
| `validation_platform` | yes | One platform that can be loaded and smoke-tested in CI |
| `chart` | no | Helm chart directory to lint |
| `smoke_test` | no | Shell-readable test receiving the built image reference |

Adding another image should require only the new directory, its manifest, and any matching chart/test files. The workflow discovers and validates all manifests automatically.

Each image manifest owns its semantic release version. Bump `images/<name>/image.json` and its matching `Chart.yaml` together, then create a GitHub Release tagged `<name>-vMAJOR.MINOR.PATCH`, for example `openbb-v0.1.0`. The generic workflow publishes only that image and chart; application dependency versions remain separate.

When an image manifest points to a chart, the same artifact-specific release also packages and publishes that chart to the repository's GHCR OCI path at `ghcr.io/<owner>/<repository>/charts/<name>`. The artifact prefix and leading `v` are removed for the Helm chart version, so release `openbb-v1.2.3` produces chart version `1.2.3`.

The generic publish workflow keeps semantic release package versions and the newly published package version. Older non-semantic CI/SHA versions are removed to bound registry storage; deploy long-lived environments by a published semantic tag or digest.
