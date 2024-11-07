FROM python:3.12.7-slim

RUN apt-get update && \
    apt-get install -y \
    g++ \
    default-jdk \
    nodejs \
    npm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt 

ENTRYPOINT ["python", "api.py"]