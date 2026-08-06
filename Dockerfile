ARG PYTHON_VERSION=3.13

# ==========================================
# Stage 1: Build Svelte 5 Frontend
# ==========================================
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

ENV CI=true

# Copy frontend dependency manifests
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies using pnpm via corepack
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm install --frozen-lockfile --ignore-scripts

# Copy frontend source code
COPY frontend/ ./

# Build static bundle (outputs to /app/frontend/build)
RUN pnpm build

# ==========================================
# Stage 2: Build Python Backend Virtual Environment
# ==========================================
FROM ghcr.io/astral-sh/uv:latest AS uv_tool
FROM python:${PYTHON_VERSION}-slim AS backend-builder
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY --from=uv_tool /uv /bin/uv

# Copy backend dependency files
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy backend source code
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# Stage 3: Final Runtime Image (Single Container)
# ==========================================
FROM python:${PYTHON_VERSION}-slim AS runtime
WORKDIR /app/backend/app

ENV PYTHONOPTIMIZE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy python virtualenv & backend source from backend-builder
COPY --from=backend-builder /app/.venv /app/.venv
COPY backend/ /app/backend/

# Copy compiled static frontend from frontend-builder into static/ inside backend
COPY --from=frontend-builder /app/frontend/build /app/backend/static

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Run database migrations & start Uvicorn server (without static access log spam)
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers --no-access-log"]




