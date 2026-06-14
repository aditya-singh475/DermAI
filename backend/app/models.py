"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionResponse(BaseModel):
    id: int
    file: str
    prediction: str
    confidence: float
    all_probabilities: dict[str, float]
    timestamp: str
    image_url: Optional[str] = None
    risk_level: Optional[str] = None
    insights: Optional[dict] = None


class PredictionHistoryItem(BaseModel):
    id: int
    filename: str
    predicted_class: str
    confidence: float
    created_at: str
    image_url: Optional[str] = None
    risk_level: Optional[str] = None


class PredictionHistoryResponse(BaseModel):
    predictions: list[PredictionHistoryItem]
    total: int
    page: int
    per_page: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
    environment: str
    classes: list[str]


class ErrorResponse(BaseModel):
    detail: str
