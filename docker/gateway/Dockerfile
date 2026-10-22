# 中継も nginx 1.27.5 の同じ公式イメージに固定。
FROM nginx:1.27.5-bookworm@sha256:6784fb0834aa7dbbe12e3d7471e69c290df3e6ba810dc38b34ae33d3c1c05f7d
RUN apt-get update \
    && apt-get install -y --no-install-recommends iptables util-linux \
    && rm -rf /var/lib/apt/lists/*
COPY --chmod=755 docker/gateway/entrypoint.sh /usr/local/bin/lab-gateway
