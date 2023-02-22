
import os
import redis
import time
from app.services import SearchService
from rq import Worker, Queue, Connection
from datetime import datetime, timedelta


def my_task():
    SearchService().run()


# Set up the Redis connection and queue
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

# Define a function to start the worker


def start_worker():
    listen = ['high', 'default', 'low']
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


# Define the time interval between each job run (in seconds)
interval = 3600

# Run the job once per hour
while True:
    # Calculate the time to run the job
    now = datetime.now()
    run_time = now + timedelta(seconds=interval)

    # Enqueue the task with arguments at the calculated time
    job = q.enqueue_in(run_time, my_task)
    print("Job enqueued with ID:", job.id)

    # Start the worker
    start_worker()

    # Wait for the specified interval
    time.sleep(interval)
