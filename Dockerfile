FROM ghcr.io/astral-sh/uv:python3.13-alpine

ARG SRC=invoice_api
ENV UV_COMPILE_BYTECODE=1
ENV UV_LOCKED=1

ENV LOGLEVEL=INFO
ENV APP_DIR=/app
ENV DATA_DIR=/data

RUN apk add weasyprint --no-cache

WORKDIR ${APP_DIR}
COPY pyproject.toml uv.lock ${APP_DIR}
RUN uv sync --no-install-project


ADD $SRC ${APP_DIR}/$SRC
COPY example-invoice.yaml ${APP_DIR}/
COPY locale/ ${APP_DIR}/locale
COPY templates/ ${APP_DIR}/templates

EXPOSE 80

CMD ["uv", "run", "--no-sync", "uvicorn", "invoice_api.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
