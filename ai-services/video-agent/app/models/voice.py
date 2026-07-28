from pydantic import BaseModel, Field


class VoiceAnalysisResult(BaseModel):
    pitchMean: float = 185.0
    pitchVariance: float = 24.5
    speechRate: float = 145.0
    clarity: float = 88.0
    confidence: float = 90.0
    json_path: str
