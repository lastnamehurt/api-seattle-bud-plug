FROM redis:latest

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
