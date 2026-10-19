# syntax=docker/dockerfile:1.7
FROM node:22.23.2-bookworm-slim@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5

ARG OPENCODE_VERSION=1.19.3

LABEL org.opencontainers.image.title="OpenCode Web" \
      org.opencontainers.image.description="Non-root OpenCode web server runtime" \
      org.opencontainers.image.source="https://github.com/buildorbit/platform-images" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${OPENCODE_VERSION}"

ENV HOME=/home/opencode \
    XDG_CONFIG_HOME=/home/opencode/.config \
    XDG_DATA_HOME=/home/opencode/.local/share \
    OPENCODE_CONFIG=/etc/opencode/opencode.json

RUN apt-get update \
    && apt-get dist-upgrade --yes \
    && npm install --global "opencode-ai@${OPENCODE_VERSION}" \
    && groupadd --gid 10001 opencode \
    && useradd --uid 10001 --gid 10001 --create-home --home-dir /home/opencode --shell /usr/sbin/nologin opencode \
    && mkdir -p /home/opencode/.local/share/opencode /etc/opencode \
    && chown -R 10001:10001 /home/opencode \
    && rm -rf /var/lib/apt/lists/*

COPY images/opencode/opencode.json /etc/opencode/opencode.json
COPY images/opencode/PUBLIC.md /etc/opencode/PUBLIC.md

USER 10001:10001
WORKDIR /workspace
EXPOSE 4096

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:4096/global/health',{headers:{Authorization:'Basic '+Buffer.from((process.env.OPENCODE_SERVER_USERNAME||'opencode')+':'+(process.env.OPENCODE_SERVER_PASSWORD||'')).toString('base64')}}).then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"]

ENTRYPOINT ["opencode"]
CMD ["web", "--port", "4096", "--hostname", "0.0.0.0"]
