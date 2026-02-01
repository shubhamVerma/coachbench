from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ModelName(str, Enum):
    CLAUDE_WEB_FREE = "claude_web_free"
    CHATGPT_WEB_FREE = "chatgpt_web_free"
    GEMINI_WEB_FREE = "gemini_web_free"
    QWEN_72B = "qwen_72b"
    DEEPSEEK_V3 = "deepseek-v3"
    GROK_4_1_FAST = "grok_4_1_fast"
    MISTRAL_LARGE = "mistral_large"


class ScenarioCategory(str, Enum):
    CAREER = "career_transitions"
    RELATIONSHIPS = "relationship_patterns"
    HABITS = "habit_formation"
    IDENTITY = "identity_perception"
    DECISIONS = "decision_making"
    MOTIVATION = "motivation_resistance"


class Message(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ModelResponse(BaseModel):
    model: ModelName
    content: str
    usage: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    response_time_ms: Optional[float] = None


class Scenario(BaseModel):
    id: str
    category: ScenarioCategory
    prompt: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    scenario_id: str
    model: ModelName
    turn1: Any
    turn2: Any
    turn3: Any
    turn2_user_response: str = Field(default="")
    turn3_user_response: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('turn1', 'turn2', 'turn3', mode='before')
    @classmethod
    def validate_turns(cls, v, info):
        if isinstance(v, dict):
            return ModelResponse(**v)
        return v


class EvaluationScores(BaseModel):
    evokes_awareness: int = Field(ge=1, le=5)
    active_listening_indicators: int = Field(ge=1, le=5)
    maintains_client_agency: int = Field(ge=1, le=5)
    question_depth_progression: int = Field(ge=1, le=5)
    client_centered_communication: int = Field(ge=1, le=5)
    ethical_boundaries: int = Field(ge=1, le=5)


class CoachingVsAdviceMoments(BaseModel):
    stayed_in_inquiry: int = Field(default=0)
    slipped_to_advice: int = Field(default=0)
    slipped_to_therapy: int = Field(default=0)
    slipped_to_consulting: int = Field(default=0)


class Evaluation(BaseModel):
    model: ModelName
    scenario_id: str
    scores: EvaluationScores
    total_score: int = Field(ge=6, le=30)  # Sum of 6 dimensions (1-5 each)
    coaching_vs_advice_moments: CoachingVsAdviceMoments
    qualitative_assessment: str
    strong_examples: List[str]
    weak_examples: List[str]
    contra_evidence: List[str]
    evaluated_at: datetime = Field(default_factory=datetime.now)


class QueryRequest(BaseModel):
    model: ModelName
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1500


class EvaluationSummary(BaseModel):
    total_scenarios: int
    total_evaluations: int
    model_averages: Dict[ModelName, Dict[str, float]]
    overall_ranking: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.now)