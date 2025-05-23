FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip

CMD ["python3"]
