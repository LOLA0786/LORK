
class RunsAPI:

    def __init__(self, replay_engine):
        self.replay_engine = replay_engine

    async def replay(self, run_id: str):
        return await self.replay_engine.replay(run_id)

    async def fork(self, run_id: str, new_run_id: str):
        return await self.replay_engine.fork(run_id, new_run_id)
