FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN  pip install --no-cache-dir -r requirements.txt


COPY . .
#create temp folder
RUN mkdir -p /app/data/temp/
RUN mkdir -p /app/data/temp/pcaps/
RUN mkdir -p /app/data/temp/yatc_dataset/
RUN mkdir -p /app/data/temp/yatc_dataset/dummy_class/
RUN mkdir -p /app/data/temp/netmamba_dataset


EXPOSE 80
CMD ["bash", "-c", "python models/finetuned_model_download.py && uvicorn main:app --host 0.0.0.0 --port 80"]
