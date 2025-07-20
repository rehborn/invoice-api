FROM python:3.13-alpine

ENV APP_DIR=/app
WORKDIR ${APP_DIR}

RUN apk add weasyprint

COPY pyproject.toml uv.lock ${APP_DIR}
RUN pip install uv && uv sync --locked

ADD src ${APP_DIR}/src
COPY example-invoice.yaml ${APP_DIR}/
COPY locale/ ${APP_DIR}/locale
COPY templates/ ${APP_DIR}/templates

RUN uv run pybabel compile -f -d locale/

WORKDIR ${APP_DIR}/src/

EXPOSE 80

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
