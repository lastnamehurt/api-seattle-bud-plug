import os
import redis
import time
from rq import Queue, Connection
from datetime import datetime, timedelta, timezone
from tasks import search_deals_task

# Set up the Redis connection and queue
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

# Define the time interval between each job run (in seconds)
interval = 3600

# Run the job once per hour
while True:
    # Calculate the time to run the job
    now = datetime.now(timezone.utc)
    run_time = now + timedelta(seconds=interval)

    # Enqueue the task with arguments at the calculated time
    job = q.enqueue_at(run_time, search_deals_task)
    print("Job enqueued with ID:", job.id)

    # Wait for the specified interval
    time.sleep(interval)
