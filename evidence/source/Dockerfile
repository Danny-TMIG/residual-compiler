FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git make \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3 -m pip install --no-cache-dir -e '.[test]'

ENV PYTHONHASHSEED=0
ENTRYPOINT ["python3", "scripts/tapesout.py"]
