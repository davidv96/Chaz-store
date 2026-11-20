#!/bin/sh
set -eu

case "$STORE_DOMAIN" in
    ""|*[!a-zA-Z0-9.-]*|.*|-*) echo "Invalid STORE_DOMAIN" >&2; exit 1 ;;
esac

runtime=/etc/nginx/store-runtime
mkdir -p "$runtime"
cp /etc/nginx/store/http.conf /etc/nginx/conf.d/default.conf
cert_dir="/etc/letsencrypt/live/$STORE_DOMAIN"

disable_https() {
    rm -f /etc/nginx/conf.d/store-https.conf
    printf '%s\n' 'location / { return 503; }' > "$runtime/http-site.conf"
}

certificate_version() {
    [ -s "$cert_dir/fullchain.pem" ] && [ -s "$cert_dir/privkey.pem" ] || return 1
    cksum < "$cert_dir/fullchain.pem"
}

enable_https() {
    envsubst '${STORE_DOMAIN}' < /etc/nginx/store/https.conf.template \
        > /etc/nginx/conf.d/store-https.conf
    printf 'location / { return 301 https://%s$request_uri; }\n' "$STORE_DOMAIN" \
        > "$runtime/http-site.conf"
}

disable_https
version=
if current=$(certificate_version); then
    if enable_https && nginx -t; then
        version=$current
    else
        disable_https
    fi
fi

(
    while sleep 30; do
        if current=$(certificate_version) && [ "$current" != "$version" ]; then
            if [ -z "$version" ]; then
                enable_https
            fi
            if nginx -t && nginx -s reload; then
                version=$current
            elif [ -z "$version" ]; then
                disable_https
            fi
        fi
    done
) </dev/null &
