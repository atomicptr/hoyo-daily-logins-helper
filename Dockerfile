FROM python:3.11 AS builder

WORKDIR /app

COPY . /app

RUN pip install poetry && \
    poetry self add "poetry-dynamic-versioning[plugin]" && \
    poetry install --without dev && \
    poetry build

FROM alpine:3.18
LABEL org.opencontainers.image.source="https://github.com/atomicptr/hoyo-daily-logins-helper"

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

COPY --from=builder /app/dist /app/dist

RUN python -m pip install dist/hoyo_daily_logins_helper-*.whl

CMD ["hoyo-daily-logins-helper"]
