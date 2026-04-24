import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from temporalio.client import Client

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
TASK_QUEUE = os.getenv("TASK_QUEUE", "default")

temporal_client: Client | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global temporal_client
    temporal_client = await Client.connect(TEMPORAL_ADDRESS)
    yield


app = FastAPI(lifespan=lifespan)


class GreetingRequest(BaseModel):
    name: str


@app.post("/greeting")
async def greeting(body: GreetingRequest):
    result = await temporal_client.execute_workflow(
        "GreetingWorkflow",
        body.name,
        id=f"greeting-{uuid.uuid4()}",
        task_queue=TASK_QUEUE,
    )
    return {"result": result}


@app.post("/waiter/{session_id}/start")
async def waiter_start(session_id: str):
    await temporal_client.start_workflow(
        "WaiterWorkflow",
        id=session_id,
        task_queue=TASK_QUEUE,
    )
    return {"session_id": session_id, "status": "running"}


@app.post("/waiter/{session_id}/stop")
async def waiter_stop(session_id: str):
    handle = temporal_client.get_workflow_handle(session_id)
    await handle.signal("stop")
    return {"session_id": session_id, "status": "signal enviado"}
