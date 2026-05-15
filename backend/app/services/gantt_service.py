from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.schemas.gantt import GanttData, GanttNode, GanttDependency


TEMPLATES: dict[str, GanttData] = {
    "labor_arbitration": GanttData(
        nodes=[
            GanttNode(id="n1", title="咨询接待", type="task", start="today", end="+3d"),
            GanttNode(id="n2", title="仲裁申请", type="milestone", start="+3d", end="+5d"),
            GanttNode(id="n3", title="举证期限", type="deadline", start="+5d", end="+20d"),
            GanttNode(id="n4", title="答辩状", type="task", start="+5d", end="+15d"),
            GanttNode(id="n5", title="证据收集", type="ai_assisted", start="+5d", end="+18d"),
            GanttNode(id="n6", title="开庭审理", type="milestone", start="+25d", end="+26d"),
            GanttNode(id="n7", title="裁决", type="milestone", start="+35d", end="+45d"),
            GanttNode(id="n8", title="执行", type="task", start="+45d", end="+60d"),
        ],
        dependencies=[
            GanttDependency(**{"from": "n1", "to": "n2"}),
            GanttDependency(**{"from": "n2", "to": "n3"}),
            GanttDependency(**{"from": "n2", "to": "n4"}),
            GanttDependency(**{"from": "n3", "to": "n6"}),
            GanttDependency(**{"from": "n6", "to": "n7"}),
            GanttDependency(**{"from": "n7", "to": "n8"}),
        ],
    ),
    "first_instance": GanttData(
        nodes=[
            GanttNode(id="n1", title="起诉准备", type="task", start="today", end="+5d"),
            GanttNode(id="n2", title="立案", type="milestone", start="+5d", end="+7d"),
            GanttNode(id="n3", title="举证", type="deadline", start="+7d", end="+25d"),
            GanttNode(id="n4", title="答辩状", type="task", start="+7d", end="+17d"),
            GanttNode(id="n5", title="证据交换", type="task", start="+20d", end="+22d"),
            GanttNode(id="n6", title="庭前准备", type="ai_assisted", start="+22d", end="+25d"),
            GanttNode(id="n7", title="一审开庭", type="milestone", start="+28d", end="+29d"),
            GanttNode(id="n8", title="法庭辩论", type="task", start="+29d", end="+30d"),
            GanttNode(id="n9", title="判决", type="milestone", start="+40d", end="+55d"),
            GanttNode(id="n10", title="执行申请", type="task", start="+55d", end="+70d"),
        ],
        dependencies=[
            GanttDependency(**{"from": "n1", "to": "n2"}),
            GanttDependency(**{"from": "n2", "to": "n3"}),
            GanttDependency(**{"from": "n2", "to": "n4"}),
            GanttDependency(**{"from": "n3", "to": "n5"}),
            GanttDependency(**{"from": "n5", "to": "n6"}),
            GanttDependency(**{"from": "n6", "to": "n7"}),
            GanttDependency(**{"from": "n7", "to": "n8"}),
            GanttDependency(**{"from": "n8", "to": "n9"}),
            GanttDependency(**{"from": "n9", "to": "n10"}),
        ],
    ),
    "second_instance": GanttData(
        nodes=[
            GanttNode(id="n1", title="上诉准备", type="task", start="today", end="+5d"),
            GanttNode(id="n2", title="上诉立案", type="milestone", start="+5d", end="+10d"),
            GanttNode(id="n3", title="阅卷", type="task", start="+10d", end="+20d"),
            GanttNode(id="n4", title="新证据提交", type="deadline", start="+10d", end="+25d"),
            GanttNode(id="n5", title="二审开庭", type="milestone", start="+30d", end="+31d"),
            GanttNode(id="n6", title="法庭辩论", type="task", start="+31d", end="+32d"),
            GanttNode(id="n7", title="终审判决", type="milestone", start="+45d", end="+60d"),
        ],
        dependencies=[
            GanttDependency(**{"from": "n1", "to": "n2"}),
            GanttDependency(**{"from": "n2", "to": "n3"}),
            GanttDependency(**{"from": "n2", "to": "n4"}),
            GanttDependency(**{"from": "n3", "to": "n5"}),
            GanttDependency(**{"from": "n5", "to": "n6"}),
            GanttDependency(**{"from": "n6", "to": "n7"}),
        ],
    ),
    "non_litigation": GanttData(
        nodes=[
            GanttNode(id="n1", title="咨询评估", type="task", start="today", end="+3d"),
            GanttNode(id="n2", title="调查取证", type="ai_assisted", start="+3d", end="+10d"),
            GanttNode(id="n3", title="方案制定", type="task", start="+10d", end="+14d"),
            GanttNode(id="n4", title="谈判协商", type="milestone", start="+14d", end="+21d"),
            GanttNode(id="n5", title="协议签署", type="milestone", start="+21d", end="+25d"),
        ],
        dependencies=[
            GanttDependency(**{"from": "n1", "to": "n2"}),
            GanttDependency(**{"from": "n2", "to": "n3"}),
            GanttDependency(**{"from": "n3", "to": "n4"}),
            GanttDependency(**{"from": "n4", "to": "n5"}),
        ],
    ),
}


def _resolve_dates(nodes: list[GanttNode]) -> list[GanttNode]:
    today = date.today()
    for node in nodes:
        for field in ("start", "end"):
            val = getattr(node, field)
            if val == "today":
                setattr(node, field, today.isoformat())
            elif val.startswith("+") and val.endswith("d"):
                days = int(val[1:-1])
                setattr(node, field, (today + timedelta(days=days)).isoformat())
    return nodes


async def get_gantt(db: AsyncSession, case_id: uuid.UUID) -> dict | None:
    stmt = select(Case.gantt_data).where(Case.id == case_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_gantt(db: AsyncSession, case_id: uuid.UUID, gantt_data: dict) -> None:
    await db.execute(update(Case).where(Case.id == case_id).values(gantt_data=gantt_data))
    await db.flush()


async def apply_template(db: AsyncSession, case: Case, template_type: str | None = None) -> dict:
    key = template_type or case.case_type
    template = TEMPLATES.get(key)
    if not template:
        raise ValueError(f"无甘特图模板: {key}")
    resolved = _resolve_dates([GanttNode(**n.model_dump()) for n in template.nodes])
    data = GanttData(nodes=resolved, dependencies=template.dependencies)
    await update_gantt(db, case.id, data.model_dump(by_alias=True))
    return data.model_dump(by_alias=True)
