# The ARC chart currently deploys runner v2.338.0. Keep this image aligned
# with the runner version used by the BuildKit runner image.
FROM node:20-bookworm-slim@sha256:2cf067cfed83d5ea958367df9f966191a942351a2df77d6f0193e162b5febfc0 AS node-toolchain
FROM ghcr.io/actions/actions-runner:2.338.0@sha256:4ffadc0002b2581327e06101fc8c06cd189232baf79fe561fac9caeb76f5e807

ARG PLAYWRIGHT_VERSION=1.55.1

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

LABEL org.opencontainers.image.title="BuildOrbit GitHub Actions CI runner" \
      org.opencontainers.image.description="Pinned GitHub Actions runner with Playwright Chromium and system dependencies" \
      org.opencontainers.image.source="https://github.com/buildorbit/platform-images" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${PLAYWRIGHT_VERSION}"

USER root

# The ARC runner base contains the runner and its action runtimes. Copy only
# the Node/npm toolchain needed to preinstall Playwright; application jobs
# still select their own Node version with actions/setup-node.
COPY --from=node-toolchain /usr/local/bin/node /usr/local/bin/node
COPY --from=node-toolchain /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm

# The Node image's npm launchers are relative links. Recreate them against the
# copied npm tree so they remain valid in the ARC runner base image.
RUN rm -f /usr/local/bin/npm /usr/local/bin/npx \
    && ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Install Chromium and its native libraries while building this immutable
# image. Fresh ARC pods therefore do not need apt access during every CI job.
RUN set -eux; \
    apt-get update; \
    apt-get install --yes --no-install-recommends ca-certificates git jq; \
    npm install --global --no-audit --no-fund "playwright@${PLAYWRIGHT_VERSION}"; \
    mkdir --parents "${PLAYWRIGHT_BROWSERS_PATH}"; \
    playwright install --with-deps chromium; \
    browser_shell="$(find "${PLAYWRIGHT_BROWSERS_PATH}" -type f -perm -111 \( -name chrome-headless-shell -o -name chrome \) | head -n 1)"; \
    test -n "${browser_shell}"; \
    test -x "${browser_shell}"; \
    ! ldd "${browser_shell}" | grep -q 'not found'; \
    chown -R runner:runner "${PLAYWRIGHT_BROWSERS_PATH}"; \
    npm cache clean --force; \
    rm -rf \
      /root/.cache \
      /var/lib/apt/lists/* \
      /home/runner/externals/node20/lib/node_modules/npm \
      /home/runner/externals/node24/lib/node_modules/npm \
      /usr/local/lib/node_modules/npm \
      /usr/local/lib/node_modules/playwright; \
    rm -f \
      /usr/local/bin/npm \
      /usr/local/bin/npx \
      /usr/local/bin/playwright \
      /home/runner/externals/node20/bin/npm \
      /home/runner/externals/node20/bin/npx \
      /home/runner/externals/node24/bin/npm \
      /home/runner/externals/node24/bin/npx \
      /usr/bin/containerd \
      /usr/bin/containerd-shim-runc-v2 \
      /usr/bin/ctr \
      /usr/bin/docker \
      /usr/bin/docker-proxy \
      /usr/bin/dockerd \
      /usr/bin/docker-init \
      /usr/bin/docker-compose \
      /usr/bin/runc \
      /usr/libexec/docker/cli-plugins/docker-buildx \
      /usr/lib/docker/cli-plugins/docker-buildx \
      /usr/local/lib/docker/cli-plugins/docker-buildx

USER runner
