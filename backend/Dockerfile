FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /opt/app

ENTRYPOINT [ "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]