# AI庭审模拟 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build AI trial simulation with multi-round debate, argument evaluation, and strategy report generation.

**Architecture:** Multi-step LangGraph execution (init→attack, evaluate→counter, report). DB tables for simulations and rounds. SSE streaming for AI responses.

**Tech Stack:** FastAPI, SQLAlchemy 2.x async, LangGraph 1.0, GLM-5.1/GLM-5-Turbo, Pydantic v2

---

### Task 1: Models + Migration

**Files:**
- Create: `backend/app/models/trial.py`
- Create: `backend/alembic/versions/e7a3b1c2d4f5_add_trial_tables.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Create trial models**

```python
# backend/app/models/trial.py
from __future__ import annotations
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseMixin

class TrialSimulation(Base, BaseMixin):
    __tablename__ = "trial_simulations"
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    mode: Mapped[str] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="active")
    rounds_completed: Mapped[int] = mapped_column(Integer, default=0)
    dispute_focus: Mapped[dict | None] = mapped_column(JSONB)
    strategy_report: Mapped[dict | None] = mapped_column(JSONB)
    rounds: Mapped[list["TrialRound"]] = relationship("TrialRound", back_populates="simulation", cascade="all, delete-orphan")

class TrialRound(Base, BaseMixin):
    __tablename__ = "trial_rounds"
    simulation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trial_simulations.id"), index=True)
    round_num: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))
    content: Mapped[str] = mapped_column(Text)
    argument_strength: Mapped[str | None] = mapped_column(String(10))
    evaluation: Mapped[dict | None] = mapped_column(JSONB)
    simulation: Mapped["TrialSimulation"] = relationship("TrialSimulation", back_populates="rounds")
```

- [ ] **Step 2: Register in __init__.py**

Add `from app.models.trial import TrialSimulation, TrialRound` to `backend/app/models/__init__.py`.

- [ ] **Step 3: Create Alembic migration**

```python
# e7a3b1c2d4f5_add_trial_tables.py
def upgrade():
    op.create_table('trial_simulations',
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('rounds_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dispute_focus', sa.JSON(), nullable=True),
        sa.Column('strategy_report', sa.JSON(), nullable=True),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'))
    op.create_table('trial_rounds',
        sa.Column('simulation_id', sa.UUID(), nullable=False),
        sa.Column('round_num', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('argument_strength', sa.String(10), nullable=True),
        sa.Column('evaluation', sa.JSON(), nullable=True),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['simulation_id'], ['trial_simulations.id']),
        sa.PrimaryKeyConstraint('id'))
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/trial.py backend/app/models/__init__.py backend/alembic/versions/e7a3b1c2d4f5_add_trial_tables.py
git commit -m "feat: add TrialSimulation and TrialRound models with migration"
```

---

### Task 2: Schemas

**Files:**
- Create: `backend/app/schemas/trial.py`

- [ ] **Step 1: Write trial schemas**

```python
# backend/app/schemas/trial.py
from __future__ import annotations
import datetime, uuid
from pydantic import BaseModel, Field

TRIAL_MODES = ("arbitration", "first_instance", "defense", "judgment")
TRIAL_ROLES = ("plaintiff", "defendant", "judge")

class TrialStartRequest(BaseModel):
    mode: str = Field(..., pattern="^(arbitration|first_instance|defense|judgment)$")
    role: str = Field(..., pattern="^(plaintiff|defendant|judge)$")

class TrialRespondRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class TrialSimulationResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    mode: str
    role: str
    status: str
    rounds_completed: int
    dispute_focus: list | None
    strategy_report: dict | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = {"from_attributes": True}

class TrialRoundResponse(BaseModel):
    id: uuid.UUID
    simulation_id: uuid.UUID
    round_num: int
    role: str
    content: str
    argument_strength: str | None
    evaluation: dict | None
    created_at: datetime.datetime
    model_config = {"from_attributes": True}

class StrategyReportResponse(BaseModel):
    dispute_focus: list[dict]
    argument_evaluation: list[dict]
    risk_points: list[dict]
    strategy_suggestions: list[dict]
    evidence_suggestions: list[dict]
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/trial.py
git commit -m "feat: add trial simulation request/response schemas"
```

---

### Task 3: AI Prompts + Graph

**Files:**
- Create: `backend/app/ai/prompts/trial_prompts.py`
- Create: `backend/app/ai/graphs/trial_graph.py`

- [ ] **Step 1: Write trial prompts**

```python
# backend/app/ai/prompts/trial_prompts.py
TRIAL_INIT_SYSTEM_PROMPT = """你是一位资深劳动法律师，正在准备庭审模拟。根据案件材料，分析并列出争议焦点。"""

TRIAL_INIT_TEMPLATE = """案件信息：
标题：{title}
类型：{case_type}
原告：{plaintiff}
被告：{defendant}
诉求金额：{claim_amount}
争议焦点：{dispute_focus}
证据：{evidences}

请列出最关键的5个争议焦点，返回JSON格式：{{"dispute_focus": ["焦点1", "焦点2", ...]}}"""

TRIAL_ATTACK_SYSTEM_PROMPT = """你是一位经验丰富的{mode}阶段{opponent_role}。你的任务是对律师的论据进行有力反驳和质疑。
要求：
1. 针对性强，抓住论据薄弱环节
2. 引用具体法条
3. 语气专业但有攻击性
4. 每次提出2-3个质疑点"""

TRIAL_ATTACK_TEMPLATE = """案件争议焦点：{dispute_focus}
当前轮次：第{round}轮
律师的论点：{user_argument}

请以{opponent_role}身份提出反驳和质疑。"""

TRIAL_EVALUATE_SYSTEM_PROMPT = """你是论据评估专家。评估律师论据的强度。返回JSON：{{"strength": "strong/medium/weak", "weaknesses": ["弱点1"], "score": 0-100}}"""

TRIAL_EVALUATE_TEMPLATE = """律师论点：{user_argument}
争议焦点：{dispute_focus}
已有质疑：{ai_challenge}

请评估此论据的强度。"""

TRIAL_COUNTER_SYSTEM_PROMPT = """你是{opponent_role}，根据律师的回应继续追问或转换攻击角度。"""

TRIAL_COUNTER_TEMPLATE = """争议焦点：{dispute_focus}
你的质疑：{ai_challenge}
律师回应：{user_response}
论据强度评估：{evaluation}

请继续追问或转换攻击角度。"""

TRIAL_REPORT_SYSTEM_PROMPT = """你是庭审策略分析师。根据模拟过程生成策略报告。返回JSON格式。"""

TRIAL_REPORT_TEMPLATE = """案件：{title}
争议焦点：{dispute_focus}
模拟轮次记录：{rounds}

请生成策略报告，JSON格式：
{{
  "dispute_focus": [{{"focus": "...", "importance": "high/medium/low"}}],
  "argument_evaluation": [{{"argument": "...", "strength": "strong/medium/weak", "score": 0-100}}],
  "risk_points": [{{"risk": "...", "level": "high/medium/low", "mitigation": "..."}}],
  "strategy_suggestions": [{{"strategy": "...", "priority": "high/medium"}}],
  "evidence_suggestions": [{{"gap": "...", "recommended_action": "..."}}]
}}"""
```

- [ ] **Step 2: Write trial graph functions (not a single StateGraph — multi-step calls)**

```python
# backend/app/ai/graphs/trial_graph.py
from __future__ import annotations
import json
from typing import TypedDict
from app.ai.graphs._client import get_openai_client
from app.ai.prompts.trial_prompts import (
    TRIAL_INIT_SYSTEM_PROMPT, TRIAL_INIT_TEMPLATE,
    TRIAL_ATTACK_SYSTEM_PROMPT, TRIAL_ATTACK_TEMPLATE,
    TRIAL_EVALUATE_SYSTEM_PROMPT, TRIAL_EVALUATE_TEMPLATE,
    TRIAL_COUNTER_SYSTEM_PROMPT, TRIAL_COUNTER_TEMPLATE,
    TRIAL_REPORT_SYSTEM_PROMPT, TRIAL_REPORT_TEMPLATE,
)

class TrialState(TypedDict, total=False):
    case_data: dict
    mode: str
    user_role: str
    dispute_focus: list[str]
    current_round: int
    ai_message: str
    user_message: str
    argument_strength: str
    evaluation: dict
    rounds: list[dict]
    strategy_report: dict
    error: str

def _get_opponent_role(mode: str, user_role: str) -> str:
    role_map = {
        ("plaintiff", "arbitration"): "被申请人代理律师",
        ("defendant", "arbitration"): "申请人代理律师",
        ("plaintiff", "first_instance"): "被告代理律师",
        ("defendant", "first_instance"): "原告代理律师",
    }
    return role_map.get((user_role, mode), "对方律师")

async def init_simulation(state: TrialState) -> TrialState:
    try:
        client = get_openai_client()
        case = state["case_data"]
        prompt = TRIAL_INIT_TEMPLATE.format(
            title=case.get("title", ""), case_type=case.get("case_type", ""),
            plaintiff=json.dumps(case.get("plaintiff", {}), ensure_ascii=False),
            defendant=json.dumps(case.get("defendant", {}), ensure_ascii=False),
            claim_amount=case.get("claim_amount", "未填写"),
            dispute_focus=", ".join(case.get("dispute_focus", [])) or "未填写",
            evidences=json.dumps(case.get("evidences", []), ensure_ascii=False),
        )
        resp = await client.chat.completions.create(
            model="glm-5-turbo", messages=[
                {"role": "system", "content": TRIAL_INIT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ], temperature=0.3, max_tokens=2048, response_format={"type": "json_object"})
        result = json.loads(resp.choices[0].message.content or "{}")
        state["dispute_focus"] = result.get("dispute_focus", [])
    except Exception as e:
        state["error"] = str(e)
    return state

async def ai_attack(state: TrialState) -> TrialState:
    try:
        client = get_openai_client()
        opponent = _get_opponent_role(state["mode"], state["user_role"])
        prompt = TRIAL_ATTACK_TEMPLATE.format(
            dispute_focus=", ".join(state.get("dispute_focus", [])),
            round=state.get("current_round", 1),
            user_argument=state.get("user_message", "律师开始陈述"),
            opponent_role=opponent,
        )
        resp = await client.chat.completions.create(
            model="glm-5.1", messages=[
                {"role": "system", "content": TRIAL_ATTACK_SYSTEM_PROMPT.format(mode=state["mode"], opponent_role=opponent)},
                {"role": "user", "content": prompt},
            ], temperature=0.7, max_tokens=2048)
        state["ai_message"] = resp.choices[0].message.content or ""
    except Exception as e:
        state["error"] = str(e)
    return state

async def evaluate_argument(state: TrialState) -> TrialState:
    try:
        client = get_openai_client()
        prompt = TRIAL_EVALUATE_TEMPLATE.format(
            user_argument=state.get("user_message", ""),
            dispute_focus=", ".join(state.get("dispute_focus", [])),
            ai_challenge=state.get("ai_message", ""),
        )
        resp = await client.chat.completions.create(
            model="glm-5-turbo", messages=[
                {"role": "system", "content": TRIAL_EVALUATE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ], temperature=0.2, max_tokens=1024, response_format={"type": "json_object"})
        content = resp.choices[0].message.content or "{}"
        result = json.loads(content)
        state["evaluation"] = result
        state["argument_strength"] = result.get("strength", "medium")
    except json.JSONDecodeError:
        state["error"] = "AI返回了无效的JSON格式"
    except Exception as e:
        state["error"] = str(e)
    return state

async def ai_counter(state: TrialState) -> TrialState:
    try:
        client = get_openai_client()
        opponent = _get_opponent_role(state["mode"], state["user_role"])
        prompt = TRIAL_COUNTER_TEMPLATE.format(
            dispute_focus=", ".join(state.get("dispute_focus", [])),
            ai_challenge=state.get("ai_message", ""),
            user_response=state.get("user_message", ""),
            evaluation=json.dumps(state.get("evaluation", {}), ensure_ascii=False),
            opponent_role=opponent,
        )
        resp = await client.chat.completions.create(
            model="glm-5.1", messages=[
                {"role": "system", "content": TRIAL_COUNTER_SYSTEM_PROMPT.format(opponent_role=opponent)},
                {"role": "user", "content": prompt},
            ], temperature=0.7, max_tokens=2048)
        state["ai_message"] = resp.choices[0].message.content or ""
    except Exception as e:
        state["error"] = str(e)
    return state

async def generate_strategy_report(state: TrialState) -> TrialState:
    try:
        client = get_openai_client()
        case = state.get("case_data", {})
        prompt = TRIAL_REPORT_TEMPLATE.format(
            title=case.get("title", ""),
            dispute_focus=json.dumps(state.get("dispute_focus", []), ensure_ascii=False),
            rounds=json.dumps(state.get("rounds", []), ensure_ascii=False),
        )
        resp = await client.chat.completions.create(
            model="glm-5.1", messages=[
                {"role": "system", "content": TRIAL_REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ], temperature=0.3, max_tokens=4096, response_format={"type": "json_object"})
        content = resp.choices[0].message.content or "{}"
        state["strategy_report"] = json.loads(content)
    except json.JSONDecodeError:
        state["error"] = "AI返回了无效的JSON格式"
    except Exception as e:
        state["error"] = str(e)
    return state
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/ai/prompts/trial_prompts.py backend/app/ai/graphs/trial_graph.py
git commit -m "feat: add trial simulation AI prompts and graph functions"
```

---

### Task 4: Service + API

**Files:**
- Create: `backend/app/services/trial_service.py`
- Create: `backend/app/api/v1/trial.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Write trial service**

```python
# backend/app/services/trial_service.py
from __future__ import annotations
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trial import TrialSimulation, TrialRound

async def create_simulation(db: AsyncSession, case_id: uuid.UUID, tenant_id: uuid.UUID, user_id: uuid.UUID, mode: str, role: str) -> TrialSimulation:
    sim = TrialSimulation(case_id=case_id, tenant_id=tenant_id, user_id=user_id, mode=mode, role=role)
    db.add(sim)
    await db.flush()
    return sim

async def get_simulation(db: AsyncSession, sim_id: uuid.UUID) -> TrialSimulation | None:
    return (await db.execute(select(TrialSimulation).where(TrialSimulation.id == sim_id))).scalar_one_or_none()

async def list_simulations(db: AsyncSession, case_id: uuid.UUID) -> list[TrialSimulation]:
    result = await db.execute(select(TrialSimulation).where(TrialSimulation.case_id == case_id).order_by(TrialSimulation.created_at.desc()))
    return list(result.scalars().all())

async def add_round(db: AsyncSession, sim_id: uuid.UUID, round_num: int, role: str, content: str, argument_strength: str | None = None, evaluation: dict | None = None) -> TrialRound:
    r = TrialRound(simulation_id=sim_id, round_num=round_num, role=role, content=content, argument_strength=argument_strength, evaluation=evaluation)
    db.add(r)
    await db.flush()
    return r

async def get_rounds(db: AsyncSession, sim_id: uuid.UUID) -> list[TrialRound]:
    result = await db.execute(select(TrialRound).where(TrialRound.simulation_id == sim_id).order_by(TrialRound.round_num))
    return list(result.scalars().all())

async def update_simulation(db: AsyncSession, sim: TrialSimulation, data: dict) -> TrialSimulation:
    for k, v in data.items():
        if v is not None:
            setattr(sim, k, v)
    await db.flush()
    return sim
```

- [ ] **Step 2: Write API endpoints**

```python
# backend/app/api/v1/trial.py
from __future__ import annotations
import json, uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User
from app.schemas.trial import TrialStartRequest, TrialRespondRequest, TrialSimulationResponse, TrialRoundResponse
from app.services import trial_service, case_service
from app.ai.graphs.trial_graph import init_simulation, ai_attack, evaluate_argument, ai_counter, generate_strategy_report

router = APIRouter(prefix="/trial", tags=["trial"])

@router.post("/cases/{case_id}/start", response_model=TrialSimulationResponse, status_code=201)
async def start_trial(case_id: uuid.UUID, req: TrialStartRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")
    sim = await trial_service.create_simulation(db, case_id, current_user.tenant_id, current_user.id, req.mode, req.role)
    # Init + first AI attack
    evidences = await case_service.list_evidences(db, case_id)
    case_data = {"title": case.title, "case_type": case.case_type, "plaintiff": case.plaintiff, "defendant": case.defendant, "claim_amount": float(case.claim_amount) if case.claim_amount else None, "dispute_focus": case.dispute_focus, "evidences": [{"title": e.title, "type": e.evidence_type} for e in evidences]}
    state = await init_simulation({"case_data": case_data, "mode": req.mode, "user_role": req.role, "error": ""})
    if state.get("error"):
        raise HTTPException(500, f"初始化失败: {state['error']}")
    await trial_service.update_simulation(db, sim, {"dispute_focus": state["dispute_focus"]})
    # First AI attack
    state["user_message"] = "律师开始陈述"
    state["current_round"] = 1
    state = await ai_attack(state)
    if state.get("error"):
        raise HTTPException(500, f"AI攻击失败: {state['error']}")
    await trial_service.add_round(db, sim.id, 1, "ai", state["ai_message"])
    await trial_service.update_simulation(db, sim, {"rounds_completed": 1})
    return TrialSimulationResponse.model_validate(sim)

@router.post("/{sim_id}/respond")
async def respond_trial(sim_id: uuid.UUID, req: TrialRespondRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sim = await trial_service.get_simulation(db, sim_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    if sim.status != "active":
        raise HTTPException(400, "模拟已结束")
    rounds = await trial_service.get_rounds(db, sim_id)
    next_round = sim.rounds_completed + 1
    # Save user response
    await trial_service.add_round(db, sim_id, next_round, "user", req.content)
    # Evaluate + counter (SSE)
    async def event_stream():
        yield f"data: {json.dumps({'status': 'evaluating'})}\n\n"
        eval_state = await evaluate_argument({"user_message": req.content, "dispute_focus": sim.dispute_focus or [], "ai_message": rounds[-1].content if rounds else "", "mode": sim.mode, "user_role": sim.role, "error": ""})
        if eval_state.get("error"):
            yield f"data: {json.dumps({'status': 'error', 'message': eval_state['error']})}\n\n"
            yield "data: [DONE]\n\n"
            return
        await trial_service.add_round(db, sim_id, next_round, "user", req.content, eval_state.get("argument_strength"), eval_state.get("evaluation"))
        yield f"data: {json.dumps({'status': 'evaluated', 'strength': eval_state.get('argument_strength'), 'evaluation': eval_state.get('evaluation')})}\n\n"
        # AI counter
        counter_state = await ai_counter({**eval_state, "rounds_completed": sim.rounds_completed, "current_round": next_round})
        if counter_state.get("error"):
            yield f"data: {json.dumps({'status': 'error', 'message': counter_state['error']})}\n\n"
        else:
            await trial_service.add_round(db, sim_id, next_round + 1, "ai", counter_state["ai_message"])
            await trial_service.update_simulation(db, sim, {"rounds_completed": next_round + 1})
            yield f"data: {json.dumps({'status': 'counter', 'content': counter_state['ai_message']})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/{sim_id}/end")
async def end_trial(sim_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sim = await trial_service.get_simulation(db, sim_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    rounds = await trial_service.get_rounds(db, sim_id)
    rounds_data = [{"round": r.round_num, "role": r.role, "content": r.content, "strength": r.argument_strength} for r in rounds]
    case = await case_service.get_case(db, sim.case_id)
    state = await generate_strategy_report({"case_data": {"title": case.title if case else ""}, "dispute_focus": sim.dispute_focus or [], "rounds": rounds_data, "error": ""})
    if state.get("error"):
        raise HTTPException(500, f"报告生成失败: {state['error']}")
    await trial_service.update_simulation(db, sim, {"status": "completed", "strategy_report": state["strategy_report"]})
    return {"simulation_id": str(sim_id), "report": state["strategy_report"]}

@router.get("/{sim_id}", response_model=TrialSimulationResponse)
async def get_trial(sim_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sim = await trial_service.get_simulation(db, sim_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    return TrialSimulationResponse.model_validate(sim)

@router.get("/{sim_id}/rounds", response_model=list[TrialRoundResponse])
async def get_trial_rounds(sim_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sim = await trial_service.get_simulation(db, sim_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    rounds = await trial_service.get_rounds(db, sim_id)
    return [TrialRoundResponse.model_validate(r) for r in rounds]

@router.get("/{sim_id}/report")
async def get_trial_report(sim_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sim = await trial_service.get_simulation(db, sim_id)
    if not sim or sim.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "模拟不存在")
    if not sim.strategy_report:
        raise HTTPException(404, "策略报告尚未生成")
    return sim.strategy_report

@router.get("/cases/{case_id}/list", response_model=list[TrialSimulationResponse])
async def list_case_trials(case_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    case = await case_service.get_case(db, case_id, current_user.tenant_id)
    if not case:
        raise HTTPException(404, "案件不存在")
    sims = await trial_service.list_simulations(db, case_id)
    return [TrialSimulationResponse.model_validate(s) for s in sims]
```

- [ ] **Step 3: Register in router.py**

Add `from app.api.v1.trial import router as trial_router` and include it in api_router.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/trial_service.py backend/app/api/v1/trial.py backend/app/api/router.py
git commit -m "feat: add trial simulation service and API endpoints"
```

---

### Task 5: Tests

**Files:**
- Create: `backend/tests/test_trial.py`

- [ ] **Step 1: Write service + schema tests**

```python
# backend/tests/test_trial.py
import pytest, uuid
from unittest.mock import AsyncMock, MagicMock, patch
from app.schemas.trial import TrialStartRequest, TrialSimulationResponse, TrialRoundResponse

def test_trial_start_request_validates_mode():
    req = TrialStartRequest(mode="arbitration", role="plaintiff")
    assert req.mode == "arbitration"

def test_trial_start_request_rejects_invalid_mode():
    with pytest.raises(Exception):
        TrialStartRequest(mode="invalid", role="plaintiff")

def test_trial_start_request_rejects_invalid_role():
    with pytest.raises(Exception):
        TrialStartRequest(mode="arbitration", role="invalid")

@pytest.mark.asyncio
async def test_create_simulation():
    from app.services.trial_service import create_simulation
    db = AsyncMock()
    db.flush = AsyncMock()
    sim = await create_simulation(db, uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), "arbitration", "plaintiff")
    assert sim.mode == "arbitration"
    assert sim.status == "active"

@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_init_simulation(MockGetClient):
    from app.ai.graphs.trial_graph import init_simulation
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = '{"dispute_focus": ["加班费计算", "经济补偿金"]}'
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await init_simulation({"case_data": {"title": "测试案件"}, "mode": "arbitration", "user_role": "plaintiff", "error": ""})
    assert len(state["dispute_focus"]) == 2

@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_ai_attack(MockGetClient):
    from app.ai.graphs.trial_graph import ai_attack
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = "我对你的加班费主张提出质疑..."
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await ai_attack({"mode": "arbitration", "user_role": "plaintiff", "current_round": 1, "user_message": "律师主张", "dispute_focus": ["加班费"], "error": ""})
    assert "质疑" in state["ai_message"]

@pytest.mark.asyncio
@patch("app.ai.graphs.trial_graph.get_openai_client")
async def test_generate_strategy_report(MockGetClient):
    import json
    from app.ai.graphs.trial_graph import generate_strategy_report
    report = {"dispute_focus": [], "argument_evaluation": [], "risk_points": [], "strategy_suggestions": [], "evidence_suggestions": []}
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = json.dumps(report)
    MockGetClient.return_value.chat.completions.create = AsyncMock(return_value=mock_resp)
    state = await generate_strategy_report({"case_data": {"title": "test"}, "dispute_focus": [], "rounds": [], "error": ""})
    assert "strategy_report" in state
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/test_trial.py -v
```

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_trial.py
git commit -m "test: add trial simulation service, schema, and AI graph tests"
```

---

### Task 6: Frontend Pages

**Files:**
- Create: `frontend/src/app/(dashboard)/trial/page.tsx`
- Create: `frontend/src/app/(dashboard)/trial/[id]/page.tsx`
- Modify: `frontend/src/app/(dashboard)/layout.tsx` (add nav item)
- Modify: `frontend/src/types/index.ts` (add trial types)

- [ ] **Step 1: Add types**

Add to `frontend/src/types/index.ts`:
```typescript
export interface TrialSimulation {
  id: string; case_id: string; mode: string; role: string; status: string;
  rounds_completed: number; dispute_focus: string[] | null; strategy_report: any;
  created_at: string; updated_at: string;
}
export interface TrialRound { id: string; simulation_id: string; round_num: number; role: string; content: string; argument_strength: string | null; evaluation: any; created_at: string; }
```

- [ ] **Step 2: Add nav item**

In `layout.tsx` navItems, add: `{ href: "/trial", label: "庭审模拟", icon: "⚖️" }`

- [ ] **Step 3: Create trial list page** — List simulations for a selected case with start button.

- [ ] **Step 4: Create trial simulation page** — Chat-style interface with SSE streaming, argument strength badges, and strategy report card.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: add trial simulation frontend pages"
```
