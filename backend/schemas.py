from datetime import datetime
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,20}$")


def validate_user_id(value: str) -> str:
    cleaned = value.strip()
    if not USER_ID_PATTERN.fullmatch(cleaned):
        raise ValueError("User ID must be 3-20 characters and use only letters, numbers, underscores, or hyphens.")
    return cleaned


def validate_display_name(value: str) -> str:
    cleaned = value.strip()
    if not 2 <= len(cleaned) <= 60:
        raise ValueError("Name must be 2-60 characters.")
    if any(char in cleaned for char in "<>{}[]"):
        raise ValueError("Name contains unsupported characters.")
    return cleaned

class PlayerCreate(BaseModel):
    student_id: str = Field(min_length=3, max_length=20)
    name: str = Field(min_length=2, max_length=60)

    @field_validator("student_id")
    @classmethod
    def valid_student_id(cls, value: str) -> str:
        return validate_user_id(value)

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        return validate_display_name(value)

class PlayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    created_at: datetime

class DNACreate(BaseModel):
    footballer_match: str
    strengths: str
    weaknesses: str
    profile_json: str

class DNAResponse(DNACreate):
    model_config = ConfigDict(from_attributes=True)

    player_id: str

class PenaltySessionCreate(BaseModel):
    player_id: str = Field(min_length=3, max_length=20)
    current_challenge: str

    @field_validator("player_id")
    @classmethod
    def valid_player_id(cls, value: str) -> str:
        return validate_user_id(value)

class PenaltySessionResponse(PenaltySessionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_at: datetime

class PenaltyAttemptCreate(BaseModel):
    session_id: int
    player_id: str = Field(min_length=3, max_length=20)
    challenge_type: str
    gesture_used: str
    result: str

    @field_validator("player_id")
    @classmethod
    def valid_player_id(cls, value: str) -> str:
        return validate_user_id(value)

class PenaltyAttemptResponse(PenaltyAttemptCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
