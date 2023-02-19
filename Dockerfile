FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set a default port number of 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Overwrite the port number with the value of the $PORT environment variable
ENTRYPOINT ["/bin/sh", "-c", "if [ \"$PORT\" ]; then exec uvicorn api:app --host 0.0.0.0 --port \"$PORT\"; else exec uvicorn api:app --host 0.0.0.0 --port 8000; fi"]
