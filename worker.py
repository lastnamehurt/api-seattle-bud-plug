import os
import time
from datetime import datetime, timedelta

import redis
from rq import Connection, Queue, Worker
from tasks import search_deals_task

# Set up the Redis connection and queue
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
conn = redis.from_url(redis_url)
q = Queue(connection=conn)


def start_worker():
    listen = ["high", "default", "low"]
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
    job = q.enqueue_in(run_time, search_deals_task)
    print("Job enqueued with ID:", job.id)

    # Start the worker
    start_worker()

    # Wait for the specified interval
    time.sleep(interval)
