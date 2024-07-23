from fastapi import UploadFile
from pydantic import BaseModel


class Assistant(BaseModel):
    userId: str
    astName: str
    astInstruction: str
    gptModel: str
    astTools: list[str]


class UpdateAssistant(BaseModel):
    userId: str
    astId: str
    astName: str
    astInstruction: str
    gptModel: str
    astTools: list[str]


class AssistantWithFile(BaseModel):
    userId: str
    astName: str
    astInstruction: str
    gptModel: str
    astTools: list[str]
    file: UploadFile


class AssistantThread(BaseModel):
    userId: str
    astId: str
    threadTitle: str


class AssistantChat(BaseModel):
    userId: str
    astId: str
    threadId: str
    message: str


class AssistantFile(BaseModel):
    fileId: str
    fileName: str
    fileSize: str
    fileType: str
