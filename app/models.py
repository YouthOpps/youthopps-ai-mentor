from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Category(str, Enum):
    scholarship = 'scholarship'
    internship = 'internship'
    fellowship = 'fellowship'
    other = 'other'


class Education(str, Enum):
    high_school = 'high_school'
    undergraduate = 'undergraduate'
    graduate = 'graduate'
    doctoral = 'doctoral'
    other = 'other'


class Profile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    age: int = Field(ge=1, le=120)
    country: str | None = Field(default=None, pattern=r'^[A-Za-z]{2}$', description='Citizenship country; omit when unknown. Never inferred from residence.')
    residence_country: str | None = Field(default=None, pattern=r'^[A-Za-z]{2}$', description='Country of residence; not used to satisfy citizenship requirements.')
    preferred_region: Literal['europe'] | None = Field(default=None, description='europe: the documented European destination list, not EU membership. Remote and unknown locations are excluded.')
    education: Education
    interests: list[str] = Field(min_length=1, max_length=20)
    opportunity_type: Category | None = Field(default=None, description='Search all types when omitted.')

    @field_validator('country', 'residence_country')
    @classmethod
    def normalize_country(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None

    @field_validator('interests')
    @classmethod
    def clean_interests(cls, values: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(value.strip().casefold() for value in values))
        if any(not value or len(value) > 80 for value in cleaned):
            raise ValueError('Each interest must be nonblank and at most 80 characters long.')
        return cleaned


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', json_schema_extra={
        'examples': [{'profile': {'age': 22, 'country': 'TR',
                     'education': 'undergraduate', 'interests': ['artificial intelligence'],
                     'opportunity_type': 'scholarship'}, 'limit': 5}]
    })
    profile: Profile
    query: str | None = Field(default=None, max_length=200)
    limit: int = Field(default=10, ge=1, le=50)


class Eligibility(BaseModel):
    description: str
    min_age: int | None = Field(default=None, ge=1)
    max_age: int | None = Field(default=None, le=120)
    countries: list[str] | None = Field(default=None, description='null: unknown; []: all countries.')
    education_levels: list[Education] | None = None


class Opportunity(BaseModel):
    id: str
    title: str
    description: str
    country: str = Field(description='Opportunity destination; not a citizenship requirement.')
    category: Category
    deadline: date | None
    interests: list[str]
    eligibility: Eligibility
    source_url: HttpUrl
    is_mock: bool = True


class Recommendation(BaseModel):
    opportunity: Opportunity
    score: int = Field(ge=0, le=100)
    reasons: list[str]
    eligibility_status: str
    warnings: list[str]
    mentor_message: str


class SearchResponse(BaseModel):
    notice: str
    is_mock: bool
    evaluated_on: date
    total: int
    results: list[Recommendation]
