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
        ("plaintiff", "defense"): "原告代理律师",
        ("defendant", "defense"): "被告代理律师",
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
        content = resp.choices[0].message.content or "{}"
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            state["error"] = "AI返回了无效的JSON格式"
            return state
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
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            state["error"] = "AI返回了无效的JSON格式"
            return state
        state["evaluation"] = result
        state["argument_strength"] = result.get("strength", "medium")
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
        try:
            state["strategy_report"] = json.loads(content)
        except json.JSONDecodeError:
            state["error"] = "AI返回了无效的JSON格式"
    except Exception as e:
        state["error"] = str(e)
    return state
