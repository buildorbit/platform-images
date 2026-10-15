# The ARC chart currently deploys runner v2.334.0. Pin the matching official
# runner image so the runner and controller remain compatible.
FROM ghcr.io/actions/actions-runner:2.334.0@sha256:b6614fce332517f74d0a76e7c762fb08e4f2ff13dcf333183397c8a5725b6e8e

ARG TARGETARCH
ARG DOCKER_VERSION=29.9.0
ARG BUILDX_VERSION=0.38.0

LABEL org.opencontainers.image.title="BuildOrbit GitHub Actions BuildKit runner" \
      org.opencontainers.image.description="Pinned Docker CLI and Buildx toolchain for rootless Kubernetes BuildKit" \
      org.opencontainers.image.source="https://github.com/buildorbit/platform-images" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${BUILDX_VERSION}"

USER root

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl git jq unzip \
    && rm -rf /var/lib/apt/lists/*

# Install the Docker CLI without a daemon. Buildx talks to the Kubernetes API
# using the runner pod's scoped ServiceAccount and creates rootless BuildKit
# workers in the dedicated buildkit namespace.
RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) docker_arch="x86_64"; buildx_arch="amd64"; buildx_sha256="4fe4cc38adf48169132749b6ca22a990928db0118e3407584ee553723115d287" ;; \
      arm64) docker_arch="aarch64"; buildx_arch="arm64"; buildx_sha256="38e890e1a162bfdbf32fbe91404991dc4fc28e55b0de901b34374a061bab4d2c" ;; \
      *) echo "unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl --fail --location --retry 3 --silent --show-error \
      --output /tmp/docker.tgz \
      "https://download.docker.com/linux/static/stable/${docker_arch}/docker-${DOCKER_VERSION}.tgz"; \
    tar --extract --file /tmp/docker.tgz --strip-components 1 --directory /usr/local/bin --no-same-owner docker/docker; \
    rm /tmp/docker.tgz; \
    curl --fail --location --retry 3 --silent --show-error \
      --output /tmp/docker-buildx \
      "https://github.com/docker/buildx/releases/download/v${BUILDX_VERSION}/buildx-v${BUILDX_VERSION}.linux-${buildx_arch}"; \
    echo "${buildx_sha256}  /tmp/docker-buildx" | sha256sum --check --status; \
    install --directory /usr/local/lib/docker/cli-plugins; \
    install --mode 0755 /tmp/docker-buildx /usr/local/lib/docker/cli-plugins/docker-buildx; \
    rm /tmp/docker-buildx; \
    docker --version; \
    docker buildx version

USER runner
