# schemas.py
from pydantic import BaseModel, Field
from typing import List


class Goal(BaseModel):
    title: str
    category: str
    deadline: str
    priority: str


class UserProfile(BaseModel):
    name: str
    language: str = "es"
    timezone: str = "America/Mexico_City"
    constraints: List[str] = Field(default_factory=list)


class CurrentState(BaseModel):
    level: str
    habits: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)


class BackendRequest(BaseModel):
    user_profile: UserProfile
    goal: Goal
    current_state: CurrentState
    user_message: str


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


class CoachPlan(BaseModel):
    plan_title: str
    summary: str
    milestones: List[Milestone]
    weekly_schedule: List[WeekPlan]
    risks: List[RiskItem]
    next_actions: List[str]