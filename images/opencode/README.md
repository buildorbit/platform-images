# OpenCode Web image

This image runs the [OpenCode](https://opencode.ai) browser interface as a
non-root process. The matching Helm chart adds a same-Pod Nginx proxy that
injects a persistent public-session banner and serves the app through one
service endpoint.

## Runtime

- OpenCode CLI package: `opencode-ai@1.19.3`.
- Web server listens on port `4096` and binds to `0.0.0.0`.
- Runs as UID/GID `10001:10001` with no Linux capabilities required.
- OpenCode sharing is disabled and `/etc/opencode/PUBLIC.md` is loaded as an
  instruction for each session.
- Session state and provider auth data live under `/home/opencode/.local/share/opencode`;
  the Helm chart persists this path with a PVC by default.
- Set `OPENCODE_SERVER_PASSWORD` using a Kubernetes Secret. OpenCode supports
  HTTP Basic authentication; the chart does not provide a default password.
- The chart can disable Basic Auth with `auth.enabled=false` when a trusted
  upstream SSO/auth layer is responsible for protecting all access.

The public-session banner is a reminder, not a security boundary or a guarantee
about model-provider data handling. Configure its wording to match the actual
service policy and provider terms.

## Build and chart validation

From the repository root:

```sh
docker build --file images/opencode/Dockerfile --tag platform-images/opencode:local .
helm lint charts/opencode --set auth.existingSecret=opencode-auth
```

## SSO

OpenCode's built-in server authentication is HTTP Basic Auth. It does not
currently provide native OIDC/SSO configuration. For SSO, put an OIDC-aware
ingress/auth proxy (for example oauth2-proxy) in front of the chart's Service,
and keep OpenCode's Basic Auth enabled as a second protection layer. Ensure
the ingress preserves WebSocket upgrades and long-lived event streams.

## Releases

The image manifest pins the upstream npm package version independently from
the platform image's semantic release version. Update the `OPENCODE_VERSION`
build argument, verify the image and chart, then release with the artifact tag
`opencode-v<image-version>`.
