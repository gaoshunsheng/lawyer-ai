from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trial import TrialSimulation, TrialRound


async def create_simulation(
    db: AsyncSession,
    case_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    mode: str,
    role: str,
) -> TrialSimulation:
    sim = TrialSimulation(
        case_id=case_id, tenant_id=tenant_id, user_id=user_id, mode=mode, role=role,
        status="active", rounds_completed=0,
    )
    db.add(sim)
    await db.flush()
    return sim


async def get_simulation(db: AsyncSession, sim_id: uuid.UUID) -> TrialSimulation | None:
    stmt = select(TrialSimulation).where(TrialSimulation.id == sim_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_simulations(db: AsyncSession, case_id: uuid.UUID) -> list[TrialSimulation]:
    stmt = (
        select(TrialSimulation)
        .where(TrialSimulation.case_id == case_id)
        .order_by(TrialSimulation.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_round(
    db: AsyncSession,
    sim_id: uuid.UUID,
    round_num: int,
    role: str,
    content: str,
    argument_strength: str | None = None,
    evaluation: dict | None = None,
) -> TrialRound:
    r = TrialRound(
        simulation_id=sim_id,
        round_num=round_num,
        role=role,
        content=content,
        argument_strength=argument_strength,
        evaluation=evaluation,
    )
    db.add(r)
    await db.flush()
    return r


async def get_rounds(db: AsyncSession, sim_id: uuid.UUID) -> list[TrialRound]:
    stmt = (
        select(TrialRound)
        .where(TrialRound.simulation_id == sim_id)
        .order_by(TrialRound.round_num)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_simulation(db: AsyncSession, sim: TrialSimulation, data: dict) -> TrialSimulation:
    for k, v in data.items():
        if v is not None:
            setattr(sim, k, v)
    await db.flush()
    return sim
