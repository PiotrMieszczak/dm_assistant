from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.assistant import Mode


class CreateConversationBody(BaseModel):
    mode: Mode = Mode.RESEARCH


class ConversationOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    id: int
    campaign_id: str = Field(alias="campaignId")
    mode: Mode
    started_at: datetime = Field(alias="startedAt")


class SendMessageBody(BaseModel):
    content: str


class MessageOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    id: int
    role: str
    content: str
    created_at: datetime = Field(alias="createdAt")
    mode: Mode
    tool_label: str | None = Field(default=None, alias="toolLabel")
