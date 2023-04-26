FROM python:3.10
LABEL org.opencontainers.image.source="https://github.com/atomicptr/hoyo-daily-logins-helper"

WORKDIR /app

COPY src /app/src
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["python", "-m", "src"]