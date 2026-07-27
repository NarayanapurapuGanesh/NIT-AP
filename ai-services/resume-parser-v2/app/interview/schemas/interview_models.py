"""
Canonical Pydantic v2 Models for Enterprise Interview Intelligence System.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport


class InterviewQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str = Field(default="Technical")  # Technical, Teaching, Research, Behavioral, Leadership
    question_text: str
    competency: str = Field(default="Problem Solving")
    difficulty: str = Field(default="Medium")  # Easy, Medium, Hard, Expert
    blooms_level: str = Field(default="Apply")  # Remember, Understand, Apply, Analyze, Evaluate, Create
    expected_duration_mins: int = 5
    expected_answer_guidelines: str = ""
    evidence_reference: Optional[str] = None


class EvaluationRubric(BaseModel):
    rubric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dimension_name: str  # Knowledge, Teaching Ability, Research Ability, Technical Skill, Communication
    description: str = ""
    level_descriptions: Dict[int, str] = Field(
        default_factory=lambda: {
            1: "Unsatisfactory",
            2: "Basic",
            3: "Proficient",
            4: "Advanced",
            5: "Expert / Exemplary",
        }
    )


class PanelMember(BaseModel):
    member_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str  # Panel Chair, Department Expert, Research Expert, Teaching Expert, External Expert
    institution: str = "NIT AP"


class InterviewRoundPlan(BaseModel):
    round_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    round_name: str  # Technical Interview, Teaching Demonstration, Research Presentation, Panel Discussion, HR Interview
    duration_mins: int = 45
    panel: List[PanelMember] = Field(default_factory=list)
    question_ids: List[str] = Field(default_factory=list)


class InterviewPlanReport(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_name: str
    position_title: str
    rounds: List[InterviewRoundPlan] = Field(default_factory=list)
    question_sets: List[InterviewQuestion] = Field(default_factory=list)
    rubrics: List[EvaluationRubric] = Field(default_factory=list)
    panel: List[PanelMember] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0


class CandidateResponseInput(BaseModel):
    question_id: str
    candidate_answer_text: str
    score: int = Field(default=3, ge=1, le=5)


class InterviewEvaluationReport(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str
    candidate_name: str
    overall_interview_score: float = Field(default=85.0, ge=0.0, le=100.0)
    category_scores: Dict[str, float] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    updated_hiring_recommendation: str = "Highly Recommended"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0


class InterviewPlanRequest(BaseModel):
    decision_report: RecruitmentDecisionReport
    department_name: Optional[str] = Field(default="Computer Science & Engineering")


class QuestionGenerationRequest(BaseModel):
    candidate_name: str
    position_title: str
    topics: List[str] = Field(default_factory=lambda: ["Data Structures", "Machine Learning"])


class EvaluationRequest(BaseModel):
    plan_id: str
    responses: List[CandidateResponseInput] = Field(default_factory=list)
