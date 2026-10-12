#!/bin/bash
set -euo pipefail

DOMAIN="${1:?Usage: tailscale-cert-renew.sh <domain>}"
CERT_DIR="/etc/ssl/tailscale/${DOMAIN}"

mkdir -p "${CERT_DIR}"

OLD_HASH=""
if [ -f "${CERT_DIR}/fullchain.pem" ]; then
    OLD_HASH=$(sha256sum "${CERT_DIR}/fullchain.pem" | awk '{print $1}')
fi

tailscale cert \
    --cert-file "${CERT_DIR}/fullchain.pem" \
    --key-file "${CERT_DIR}/privkey.pem" \
    "${DOMAIN}"

NEW_HASH=$(sha256sum "${CERT_DIR}/fullchain.pem" | awk '{print $1}')

if [ "${OLD_HASH}" != "${NEW_HASH}" ]; then
    echo "Cert for ${DOMAIN} changed, reloading caddy"
    docker exec caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile 2>/dev/null || true
fi
