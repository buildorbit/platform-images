# OpenCode Helm chart

The chart runs OpenCode and a same-Pod Nginx banner proxy. The Service exposes
only Nginx; OpenCode's port is not published. It enables persistent session
and workspace storage by default, and requires an existing Secret for OpenCode's
HTTP Basic Auth.

Basic Auth is enabled by default. To disable it, set `auth.enabled=false` only
when another trusted control enforces authentication and direct access to the
Service and pod is restricted. Without another auth layer, anyone who can
reach the web server can use it.

Create the secret outside Helm (use your cluster's secret-management workflow):

```sh
kubectl create secret generic opencode-auth \
  --from-file=username=/secure/path/opencode-username \
  --from-file=password=/secure/path/opencode-password
```

Install locally:

```sh
helm upgrade --install opencode ./charts/opencode \
  --set auth.existingSecret=opencode-auth
```

For an ingress, configure your ingress controller with TLS and, if desired,
OIDC authentication such as oauth2-proxy. Preserve WebSocket upgrades and
long-lived event streams. OpenCode Basic Auth remains active behind the SSO
layer by default. To let the ingress SSO layer handle authentication, set
`auth.enabled=false` and ensure users cannot bypass the ingress to reach the
Service. The chart's built-in Ingress is optional and does not configure SSO.

The OpenCode container uses a read-only root filesystem. Persistent session data
and workspace files are stored on PVCs. Runtime state, configuration, cache,
temporary files, and lock files use ephemeral `emptyDir` mounts; runtime locks
must not be persisted across pod replacements.

For production, use the published OCI chart and an immutable image digest:

```sh
helm upgrade --install opencode oci://ghcr.io/buildorbit/platform-images/charts/opencode \
  --version 0.1.1 \
  --set auth.existingSecret=opencode-auth \
  --set image.repository=ghcr.io/buildorbit/platform-images/opencode \
  --set image.digest=sha256:<published-digest>
```

Session data, including OpenCode provider credentials added through its auth
flow, is stored on the PVC. Protect the PVC and backups accordingly. The
default banner is configurable through `banner.text`; word it to reflect the
actual data handling policy.
