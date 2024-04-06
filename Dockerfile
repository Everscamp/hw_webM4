FROM python:3.12.0-alpine

WORKDIR /app

VOLUME ["/app/storage"]

COPY . .

EXPOSE 3000
EXPOSE 5000

ENTRYPOINT ["python", "main.py"]
