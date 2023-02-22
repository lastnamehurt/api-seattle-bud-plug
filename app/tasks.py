import os
import redis
import time
from rq import Queue
from datetime import datetime, timedelta

# Define a function that performs a task
def my_task(x, y):
    return x + y

# Set up the Redis connection and queue
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

# Define the time interval between each job run (in seconds)
interval = 3600

# Run the job once per hour
while True:
    # Calculate the time to run the job
    now = datetime.now()
    run_time = now + timedelta(seconds=interval)

    # Enqueue the task with arguments at the calculated time
    job = q.enqueue_in(run_time, my_task, 1, 2)
    print("Job enqueued with ID:", job.id)

    # Wait for the specified interval
    time.sleep(interval)
