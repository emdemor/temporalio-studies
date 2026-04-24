from datetime import datetime

from temporalio import activity


@activity.defn
async def format_greeting(name: str) -> str:
    now = datetime.now().strftime("%H:%M:%S")
    return f"Olá, {name}! São {now}."
