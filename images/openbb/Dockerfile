# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e

# Digest is the official Python 3.12 slim-bookworm multi-platform manifest.
# The image is built for linux/amd64 in CI.
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e

ARG OPENBB_VERSION=4.7.2
ARG OPENBB_PLATFORM_API_VERSION=1.3.6

LABEL org.opencontainers.image.title="OpenBB Platform API" \
      org.opencontainers.image.description="Curated, non-root OpenBB Platform API image" \
      org.opencontainers.image.source="https://github.com/buildorbit/platform-images" \
      org.opencontainers.image.licenses="AGPL-3.0-only,Apache-2.0" \
      org.opencontainers.image.version="${OPENBB_VERSION}" \
      io.buildorbit.openbb.platform-api-version="${OPENBB_PLATFORM_API_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/openbb \
    OPENBB_API_HOST=0.0.0.0 \
    OPENBB_API_PORT=6900

WORKDIR /opt/openbb

COPY images/openbb/requirements.txt /tmp/openbb-requirements.txt

RUN python -m pip install --no-cache-dir --requirement /tmp/openbb-requirements.txt \
    && rm -f /tmp/openbb-requirements.txt \
    && groupadd --gid 10001 openbb \
    && useradd --uid 10001 --gid 10001 --create-home --home-dir /home/openbb --shell /usr/sbin/nologin openbb \
    && mkdir -p /opt/openbb/assets /home/openbb/OpenBBUserData /tmp/openbb-cache \
    && chown -R 10001:10001 /opt/openbb /home/openbb /tmp/openbb-cache

COPY --chmod=0555 images/openbb/scripts/build-metadata.py /usr/local/bin/build-openbb-metadata

# Generate widgets.json once while building the image. Runtime uses --no-build,
# avoiding an expensive and network-independent metadata build on every start.
RUN /usr/local/bin/build-openbb-metadata --output /opt/openbb/assets/widgets.json \
    && chown 10001:10001 /opt/openbb/assets/widgets.json

USER 10001:10001

EXPOSE 6900

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=5 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:6900/docs', timeout=3)"]

ENTRYPOINT ["openbb-api", "--no-build", "--widgets-json", "/opt/openbb/assets/widgets.json", "--apps-json", "/home/openbb/OpenBBUserData/workspace_apps.json"]
