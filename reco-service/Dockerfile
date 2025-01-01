FROM python:3.10-slim as base

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /app
COPY ./src .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]