from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.trial import (
    TrialRespondRequest,
    TrialRoundResponse,
    TrialSimulationResponse,
    TrialStartRequest,
)
from app.ai.graphs.trial_graph import (
    ai_attack,
    ai_counter,
    evaluate_argument,
    generate_strategy_report,
    init_simulation,
)
from app.services import trial_service, case_service

router = APIRouter(prefix="/trial", tags=["trial"])


@router.get("/list", response_model=list[TrialSimulationResponse])
async def list_trials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sims = await trial_service.list_all_simulations(db, current_user.tenant_id)
    return [TrialSimulationResponse.model_validate(s) for s in sims]


@router.post("/cases/{case_id}/start", response_model=TrialSimulationResponse, status_code=201)
async def start_trial(
    case_id: uuid.UUID,
    req: TrialStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")

    sim = await trial_service.create_simulation(
        db, case_id, current_user.tenant_id, current_user.id, req.mode, req.role,
    )

    evidences = await case_service.list_evidences(db, case_id)
    case_data = {
        "title": case.title,
        "case_type": case.case_type,
        "plaintiff": case.plaintiff,
        "defendant": case.defendant,
        "claim_amount": float(case.claim_amount) if case.claim_amount else None,
        "dispute_focus": case.dispute_focus,
        "evidences": [{"title": e.title, "type": e.evidence_type} for e in evidences],
    }

    state = await init_simulation({
        "case_data": case_data, "mode": req.mode, "user_role": req.role, "error": "",
    })
    if state.get("error"):
        raise HTTPException(500, f"初始化失败: {state['error']}")

    await trial_service.update_simulation(db, sim, {"dispute_focus": state.get("dispute_focus", [])})

    state["user_message"] = "律师开始陈述"
    state["current_round"] = 1
    state = await ai_attack(state)
    if state.get("error"):
        raise HTTPException(500, f"AI攻击失败: {state['error']}")

    await trial_service.add_round(db, sim.id, 1, "ai", state["ai_message"])
    await trial_service.update_simulation(db, sim, {"rounds_completed": 1})
    return TrialSimulationResponse.model_validate(sim)


@router.post("/{sim_id}/respond")
async def respond_trial(
    sim_id: uuid.UUID,
    req: TrialRespondRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sim = await trial_service.get_simulation(db, sim_id, tenant_id=current_user.tenant_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    if sim.status != "active":
        raise HTTPException(400, "模拟已结束")

    rounds = await trial_service.get_rounds(db, sim_id, tenant_id=current_user.tenant_id)
    next_round = sim.rounds_completed + 1

    async def event_stream():
        yield f"data: {json.dumps({'status': 'evaluating'})}\n\n"

        eval_state = await evaluate_argument({
            "user_message": req.content,
            "dispute_focus": sim.dispute_focus or [],
            "ai_message": rounds[-1].content if rounds else "",
            "mode": sim.mode,
            "user_role": sim.role,
            "error": "",
        })
        if eval_state.get("error"):
            yield f"data: {json.dumps({'status': 'error', 'message': eval_state['error']})}\n\n"
            yield "data: [DONE]\n\n"
            return

        await trial_service.add_round(
            db, sim_id, next_round, "user", req.content,
            eval_state.get("argument_strength"), eval_state.get("evaluation"),
        )

        yield f"data: {json.dumps({'status': 'evaluated', 'strength': eval_state.get('argument_strength'), 'evaluation': eval_state.get('evaluation')})}\n\n"

        counter_state = await ai_counter({
            **eval_state,
            "rounds_completed": sim.rounds_completed,
            "current_round": next_round,
        })
        if counter_state.get("error"):
            yield f"data: {json.dumps({'status': 'error', 'message': counter_state['error']})}\n\n"
        else:
            await trial_service.add_round(db, sim_id, next_round + 1, "ai", counter_state["ai_message"])
            await trial_service.update_simulation(db, sim, {"rounds_completed": next_round + 1})
            yield f"data: {json.dumps({'status': 'counter', 'content': counter_state['ai_message']})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{sim_id}/end")
async def end_trial(
    sim_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sim = await trial_service.get_simulation(db, sim_id, tenant_id=current_user.tenant_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")

    rounds = await trial_service.get_rounds(db, sim_id, tenant_id=current_user.tenant_id)
    rounds_data = [
        {"round": r.round_num, "role": r.role, "content": r.content, "strength": r.argument_strength}
        for r in rounds
    ]
    case = await case_service.get_case(db, sim.case_id)
    state = await generate_strategy_report({
        "case_data": {"title": case.title if case else ""},
        "dispute_focus": sim.dispute_focus or [],
        "rounds": rounds_data,
        "error": "",
    })
    if state.get("error"):
        raise HTTPException(500, f"报告生成失败: {state['error']}")

    await trial_service.update_simulation(db, sim, {"status": "completed", "strategy_report": state["strategy_report"]})
    return {"simulation_id": str(sim_id), "report": state["strategy_report"]}


@router.get("/{sim_id}", response_model=TrialSimulationResponse)
async def get_trial(
    sim_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sim = await trial_service.get_simulation(db, sim_id, tenant_id=current_user.tenant_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    return TrialSimulationResponse.model_validate(sim)


@router.get("/{sim_id}/rounds", response_model=list[TrialRoundResponse])
async def get_trial_rounds(
    sim_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sim = await trial_service.get_simulation(db, sim_id, tenant_id=current_user.tenant_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    rounds = await trial_service.get_rounds(db, sim_id, tenant_id=current_user.tenant_id)
    return [TrialRoundResponse.model_validate(r) for r in rounds]


@router.get("/{sim_id}/report")
async def get_trial_report(
    sim_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sim = await trial_service.get_simulation(db, sim_id, tenant_id=current_user.tenant_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    if not sim.strategy_report:
        raise HTTPException(404, "策略报告尚未生成")
    return sim.strategy_report


@router.get("/cases/{case_id}/list", response_model=list[TrialSimulationResponse])
async def list_case_trials(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")
    sims = await trial_service.list_simulations(db, case_id, tenant_id=current_user.tenant_id)
    return [TrialSimulationResponse.model_validate(s) for s in sims]
