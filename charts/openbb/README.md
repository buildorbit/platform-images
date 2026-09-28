# OpenBB Helm chart

This chart deploys the non-root OpenBB Platform API image on port 6900. It enables Kubernetes probes against `/docs`, drops all Linux capabilities, disables privilege escalation, and disables service-account token mounting.

Published releases are available as OCI Helm charts. The chart version follows the OpenBB artifact release tag, for example `openbb-v0.1.0` publishes chart version `0.1.0`:

```sh
helm upgrade --install openbb oci://ghcr.io/buildorbit/platform-images/charts/openbb \
  --version 0.1.0 \
  --set image.repository=ghcr.io/buildorbit/platform-images/openbb \
  --set image.digest=sha256:<published-digest>
```

Use an immutable image digest for production:

```sh
helm upgrade --install openbb ./charts/openbb \
  --set image.digest=sha256:<published-digest>
```

The chart supports a tag for local development, but `image.digest` takes precedence over `image.tag` when both are set.
