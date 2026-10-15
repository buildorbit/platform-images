# The ARC chart currently deploys runner v2.334.0. Pin the matching official
# runner image so the runner and controller remain compatible.
FROM ghcr.io/actions/actions-runner:2.334.0@sha256:b6614fce332517f74d0a76e7c762fb08e4f2ff13dcf333183397c8a5725b6e8e

ARG TARGETARCH
ARG DOCKER_VERSION=29.9.0

LABEL org.opencontainers.image.title="BuildOrbit GitHub Actions BuildKit runner" \
      org.opencontainers.image.description="Pinned daemonless Docker CLI for rootless Kubernetes BuildKit workflows" \
      org.opencontainers.image.source="https://github.com/buildorbit/platform-images" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${DOCKER_VERSION}"

USER root

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl git jq unzip \
    && rm -rf /var/lib/apt/lists/*

# Install the Docker CLI without a daemon. Workflows install a pinned Buildx
# action at job time; that keeps the runner image small and lets CI refresh the
# build client independently from the runner lifecycle.
RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) docker_arch="x86_64" ;; \
      arm64) docker_arch="aarch64" ;; \
      *) echo "unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl --fail --location --retry 3 --silent --show-error \
      --output /tmp/docker.tgz \
      "https://download.docker.com/linux/static/stable/${docker_arch}/docker-${DOCKER_VERSION}.tgz"; \
    tar --extract --file /tmp/docker.tgz --strip-components 1 --directory /usr/local/bin --no-same-owner docker/docker; \
    rm /tmp/docker.tgz; \
    # The upstream ARC runner base may ship a system Buildx plugin. Remove it
    # so the workflow-controlled, patched version is the only Buildx client.
    rm -f \
      /usr/libexec/docker/cli-plugins/docker-buildx \
      /usr/lib/docker/cli-plugins/docker-buildx \
      /usr/local/lib/docker/cli-plugins/docker-buildx; \
    docker --version

USER runner
