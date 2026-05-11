from pydantic import BaseModel, Field
from typing import Literal, List, Optional


# ===== INPUT DESDE BACKEND =====

class MessagePart(BaseModel):
    type: str = "text"
    text: Optional[str] = None


class Message(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    parts: List[MessagePart]


class ChatPayload(BaseModel):
    id: str
    messages: List[Message]
    trigger: str
    user_name: Optional[str] = None
    age: Optional[int] = None
    token: Optional[str] = None
    ai_settings: Optional[dict] = None


# ===== OUTPUT DEL ROUTER =====

class RouterDecision(BaseModel):
    route: Literal["planner", "qa", "fallback"]
    reason: str


# ===== OUTPUT DEL COACH =====

class SessionItem(BaseModel):
    day: str
    task: str
    duration_min: int


class WeekPlan(BaseModel):
    week: int
    sessions: List[SessionItem]


class Milestone(BaseModel):
    week: int
    target: str


class RiskItem(BaseModel):
    risk: str
    mitigation: str


class CoachResponse(BaseModel):
    response_type: Literal["plan", "answer", "fallback"]
    message_for_user: str
    plan_title: Optional[str] = None
    summary: str
    milestones: List[Milestone] = Field(default_factory=list)
    weekly_schedule: List[WeekPlan] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)