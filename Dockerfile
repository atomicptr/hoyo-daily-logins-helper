FROM python:3.11 AS builder

WORKDIR /app

COPY . /app

RUN pip install build && \
    python -m build --sdist --wheel --outdir dist/ .

FROM python:3.11-slim
LABEL org.opencontainers.image.source="https://github.com/atomicptr/hoyo-daily-logins-helper"

WORKDIR /app

COPY --from=builder /app/dist /app/dist

RUN pip install dist/hoyo_daily_logins_helper-*.whl

CMD ["hoyo-daily-logins-helper"]
