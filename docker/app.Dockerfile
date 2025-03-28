FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

COPY docker/entrypoint.sh /app/
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
