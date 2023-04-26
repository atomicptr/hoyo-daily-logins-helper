FROM python:3.10

WORKDIR /app

COPY src /app/src
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["python", "-m", "src"]