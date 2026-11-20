#!/bin/sh
set -eu

: "${LETSENCRYPT_EMAIL:?Set LETSENCRYPT_EMAIL in .env}"
cert_dir="/etc/letsencrypt/live/$STORE_DOMAIN"

trap 'exit 0' TERM INT

pause() {
    sleep "$1" &
    wait "$!"
}

while :; do
    if [ -s "$cert_dir/fullchain.pem" ] && [ -s "$cert_dir/privkey.pem" ]; then
        certbot renew --non-interactive --cert-name "$STORE_DOMAIN" || true
        pause 43200
    else
        certbot certonly --non-interactive --agree-tos --email "$LETSENCRYPT_EMAIL" \
            --webroot --webroot-path /var/www/acme --cert-name "$STORE_DOMAIN" \
            -d "$STORE_DOMAIN" || pause 3600
    fi
done
