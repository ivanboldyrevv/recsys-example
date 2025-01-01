FROM nvidia/cuda:11.8.0-base-ubuntu22.04

RUN apt-get update && \
    apt-get install -y \
        git \
        python3-pip \
        python3-dev \
        libglib2.0-0

COPY requirements.txt requirements.txt

RUN python3 -m pip install --no-cache-dir numpy==1.26.4
RUN python3 -m pip install --no-cache-dir torch==2.0.0 --index-url https://download.pytorch.org/whl/cu118
RUN python3 -m pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .

CMD ["python3", "main.py"]
