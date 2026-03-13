from dataclasses import dataclass
from datetime import datetime
from typing import Any, List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class RunEvent:
    run_id: UUID
    sequence: int
    timestamp: datetime
    type: str
    agent_id: str
    payload: dict[str, Any]


class EventStore:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, event: RunEvent):

        stmt = sa.text("""
        INSERT INTO run_events (
            run_id,
            sequence,
            timestamp,
            type,
            agent_id,
            payload
        )
        VALUES (
            :run_id,
            :sequence,
            :timestamp,
            :type,
            :agent_id,
            :payload::jsonb
        )
        """)

        await self.session.execute(stmt, {
            "run_id": str(event.run_id),
            "sequence": event.sequence,
            "timestamp": event.timestamp,
            "type": event.type,
            "agent_id": event.agent_id,
            "payload": event.payload
        })

        await self.session.commit()

    async def get_run_events(self, run_id: str) -> List[RunEvent]:

        stmt = sa.text("""
        SELECT run_id, sequence, timestamp, type, agent_id, payload
        FROM run_events
        WHERE run_id = :run_id
        ORDER BY sequence ASC
        """)

        result = await self.session.execute(stmt, {"run_id": run_id})
        rows = result.fetchall()

        return [
            RunEvent(
                run_id=row.run_id,
                sequence=row.sequence,
                timestamp=row.timestamp,
                type=row.type,
                agent_id=row.agent_id,
                payload=row.payload
            )
            for row in rows
        ]
