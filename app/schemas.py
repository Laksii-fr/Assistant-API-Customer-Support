from datetime import datetime
from pydantic import BaseModel
import app.models.model_type as model_type


class CreateAssistantBaseSchema(BaseModel):
    astId: str
    astName: str
    astInstruction: str
    gptModel: str
    astTools:  list[str]
    astFiles:  list[model_type.AssistantFile]
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class CreateAssistantThreadBaseSchema(BaseModel):
    astId: str
    threadId: str
    threadTitle: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None