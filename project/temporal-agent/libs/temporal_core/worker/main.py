import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker
from activities.greeting import format_greeting
from workflows.greeting import GreetingWorkflow
from workflows.waiter import WaiterWorkflow

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
TASK_QUEUE = os.getenv("TASK_QUEUE", "default")


async def main():
    client = await Client.connect(TEMPORAL_ADDRESS)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[GreetingWorkflow, WaiterWorkflow],
        activities=[format_greeting],
    )
    print(f"Worker iniciado — fila: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
