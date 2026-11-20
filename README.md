# Custom Store

## Run locally with Docker Compose

```sh
make dev
```

Open Django directly at http://localhost:8000. The local stack runs Django's development server and a Tailwind watcher. Both mount `app/`, so Python, template, and CSS edits are reflected without rebuilding. Django applies migrations on startup and creates the local admin account (`admin@example.com` / `password`) if that email is missing. Set `SUPERUSER_EMAIL` and `SUPERUSER_PASSWORD` in `.env.development` to override those defaults.

If port 8000 is occupied, run `make dev PORT=8001` or set `DJANGO_PORT` in `.env.development`. Run `make down` to stop the development stack and keep its SQLite database and uploads.

## Deploy with Let's Encrypt

Use Docker Compose 2.24.4 or later. Point the domain's DNS records at the host and allow inbound TCP ports 80 and 443. Copy `.env.example` to `.env`, set `STORE_DOMAIN` and `LETSENCRYPT_EMAIL`, and generate a value for `DJANGO_SECRET_KEY` with `openssl rand -hex 32`.

```sh
make prod
docker compose --env-file .env -f docker-compose.prod.yml logs -f nginx certbot
```

Production uses `docker-compose.prod.yml` as a standalone stack. The web image builds Tailwind from the npm lockfile. On startup, Django applies migrations and collects static files before starting Gunicorn with debug disabled. nginx publishes ports 80 and 443, serves static files and uploads, and proxies application requests to Gunicorn over the internal Docker network.

During initial issuance, nginx serves the ACME challenge over HTTP and returns 503 for other requests. Once Certbot writes the certificate, nginx enables HTTPS and redirects HTTP traffic within about 30 seconds. Certbot checks for renewal twice a day, and nginx reloads when the certificate changes. Run `make prod-down` to stop the stack and keep the data and certificates.

## Import existing local data

Development and production use separate named volumes. To import an existing database and uploads into a fresh production deployment, stop any local Django process using the database and run the following from the repository root. The database import refuses to overwrite an existing volume database.

```sh
prod_compose() {
    docker compose --env-file .env -f docker-compose.prod.yml "$@"
}
prod_compose build web
prod_compose run --rm --no-deps -T web sh -c 'set -C; cat > /data/db/db.sqlite3' < app/db.sqlite3
tar -C app/media -cf - . | prod_compose run --rm --no-deps -T web tar -xf - -C /data/media
make prod
```

Skip the media import if you have no uploads. Back up the database and media volumes before deleting them.
