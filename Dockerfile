FROM node:24-bookworm-slim AS tailwind
WORKDIR /app/theme/static_src
COPY app/theme/static_src/package*.json ./
RUN npm ci
COPY app/ /app/
RUN npm run build

FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS python
ENV UV_PYTHON_DOWNLOADS=0 UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/opt/store/.venv/bin:$PATH"
WORKDIR /opt/store
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

RUN groupadd --gid 10001 store \
    && useradd --uid 10001 --gid store --no-create-home store \
    && install -d -o store -g store /data/db /data/media /data/static
WORKDIR /app
USER store

FROM python AS development
COPY docker/dev/web.sh /opt/store/dev-web.sh
CMD ["sh", "/opt/store/dev-web.sh"]

FROM python AS production
COPY app/ ./
COPY --from=tailwind /app/theme/static/css/dist/ ./theme/static/css/dist/
COPY entrypoint.sh /opt/store/entrypoint.sh
CMD ["sh", "/opt/store/entrypoint.sh"]
