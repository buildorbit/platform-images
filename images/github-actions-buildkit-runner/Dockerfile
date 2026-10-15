# The ARC chart currently deploys runner v2.338.0. Pin the matching official
# runner image so the runner and controller remain compatible.
FROM ghcr.io/actions/actions-runner:2.338.0@sha256:4ffadc0002b2581327e06101fc8c06cd189232baf79fe561fac9caeb76f5e807

ARG TARGETARCH
ARG DOCKER_VERSION=29.9.0

LABEL org.opencontainers.image.title="BuildOrbit GitHub Actions BuildKit runner" \
      org.opencontainers.image.description="Pinned daemonless Docker CLI for rootless Kubernetes BuildKit workflows" \
      org.opencontainers.image.source="https://github.com/buildorbit/platform-images" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${DOCKER_VERSION}"

USER root

RUN apt-get update \
    && apt-get dist-upgrade --yes \
    && apt-get install --yes --no-install-recommends ca-certificates curl git jq unzip \
    && rm -rf /var/lib/apt/lists/*

# The upstream runner currently bundles a vulnerable undici release in its
# Node 24 npm installation. Keep the runner base pinned, but replace only this
# dependency with the fixed release. Download and verify the package directly
# so npm does not reinstall or execute lifecycle scripts from its full tree.
RUN set -eux; \
    undici_root=/home/runner/externals/node24/lib/node_modules/npm/node_modules/undici; \
    tmp_dir="$(mktemp -d)"; \
    curl --fail --location --retry 3 --silent --show-error \
      --output "$tmp_dir/undici.tgz" \
      https://registry.npmjs.org/undici/-/undici-6.28.1.tgz; \
    echo 'e18191aac9c0ff43dac7fe9b10b7041a22d07addb7b66a6e8ac14a52a5b69b74  '"$tmp_dir/undici.tgz" | sha256sum --check --status; \
    rm -rf "$undici_root"; \
    mkdir -p "$undici_root"; \
    tar --extract --file "$tmp_dir/undici.tgz" --strip-components 1 --directory "$undici_root" --no-same-owner; \
    chown -R runner:runner "$undici_root"; \
    rm -rf "$tmp_dir"

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
      /usr/bin/containerd \
      /usr/bin/containerd-shim-runc-v2 \
      /usr/bin/ctr \
      /usr/bin/docker \
      /usr/bin/dockerd \
      /usr/bin/docker-init \
      /usr/bin/docker-compose \
      /usr/bin/docker-proxy \
      /usr/bin/runc \
      /usr/libexec/docker/cli-plugins/docker-buildx \
      /usr/lib/docker/cli-plugins/docker-buildx \
      /usr/local/lib/docker/cli-plugins/docker-buildx; \
    docker --version

USER runner
