from __future__ import annotations

import uuid
from pydantic import BaseModel, Field

NODE_TYPES = ("deadline", "milestone", "task", "ai_assisted")
NODE_STATUSES = ("pending", "in_progress", "completed", "overdue")


class GanttNode(BaseModel):
    id: str
    title: str
    type: str = Field(..., pattern="^(deadline|milestone|task|ai_assisted)$")
    start: str
    end: str
    assignee_id: str | None = None
    status: str = Field("pending", pattern="^(pending|in_progress|completed|overdue)$")
    progress: int = Field(0, ge=0, le=100)
    description: str | None = None


class GanttDependency(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    type: str = "finish_to_start"


class GanttData(BaseModel):
    nodes: list[GanttNode] = []
    dependencies: list[GanttDependency] = []

    model_config = {"populate_by_name": True}


class GanttUpdateRequest(BaseModel):
    gantt_data: GanttData
