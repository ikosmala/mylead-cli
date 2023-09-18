from datetime import date, datetime, timedelta
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, validator


class Api(BaseModel):
    token: str
    limit: Literal[10, 20, 50, 100, 500] = 500
    date_to: date = Field(default_factory=lambda: date.today())
    date_from: date = Field(default_factory=lambda: date.today() - timedelta(days=365))
    status: Literal["approved", "pending", "rejected", "pre_approved"] | None = None

    @validator("date_to", pre=True)
    def strip_date_to(cls, value):
        return value.date()

    @validator("date_from", pre=True)
    def strip_date_from(cls, value):
        return value.date()


class UserAgent(BaseModel):
    name: str
    operation_system: str
    operation_system_version: str
    browser_system: str
    browser_version: str
    device: Literal["mobile", "desktop", "tablet"]
    device_brand: str | None
    device_model: str | None


class CreatedAt(BaseModel):
    date: datetime
    timezone_type: int
    timezone: str


class Lead(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    lead_id: str = Field(alias="id", frozen=True)
    campaign_id: int = Field(gt=0, frozen=True)
    campaign_name: str
    payout: float = Field(ge=0)
    currency: str
    status: Literal["approved", "pending", "rejected", "pre_approved"]
    status_reason: str | None
    country: str
    created_at: CreatedAt
    user_agent: UserAgent
    ip: str
    ml_sub1: str | None
    ml_sub2: str | None
    ml_sub3: str | None
    ml_sub4: str | None
    ml_sub5: str | None
