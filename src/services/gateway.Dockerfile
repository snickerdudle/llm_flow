FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir nameko

CMD ["nameko", "run", "--config", "config.yaml", "gateway_service"]