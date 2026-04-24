from datetime import timedelta
from temporalio import workflow


@workflow.defn
class WaiterWorkflow:
    def __init__(self):
        self.should_stop = False

    @workflow.run
    async def run(self) -> str:
        while not self.should_stop:
            workflow.logger.info("ainda rodando...")
            await workflow.sleep(timedelta(seconds=1))
        return "encerrado via signal"

    @workflow.signal
    async def stop(self) -> None:
        self.should_stop = True
