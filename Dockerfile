FROM node:24-bookworm-slim AS tailwind
WORKDIR /app/theme/static_src
COPY app/theme/static_src/package*.json ./
RUN npm ci
COPY app/ /app/

FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS python
ENV UV_PYTHON_DOWNLOADS=0 UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/opt/store/.venv/bin:$PATH"
WORKDIR /opt/store
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python AS assets
COPY --from=tailwind /usr/local/bin/node /usr/local/bin/node
COPY --from=tailwind /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
COPY --from=tailwind /app /app
WORKDIR /app
RUN python manage.py tailwind build

FROM python AS runtime
RUN groupadd --gid 10001 store \
    && useradd --uid 10001 --gid store --no-create-home store \
    && install -d -o store -g store /data/db /data/media /data/static
WORKDIR /app
COPY app/ ./
COPY --from=assets /app/theme/static/css/dist/ ./theme/static/css/dist/
USER store
COPY deploy/start.sh /opt/store/start.sh
CMD ["sh", "/opt/store/start.sh"]
