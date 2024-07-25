from fastapi import UploadFile
from pydantic import BaseModel


class Assistant(BaseModel):
    astName: str
    astInstruction: str
    gptModel: str
    astTools: list[str]


class UpdateAssistant(BaseModel):
    astId: str
    astName: str
    astInstruction: str
    gptModel: str
    astTools: list[str]


class AssistantWithFile(BaseModel):
    astName: str
    astInstruction: str
    gptModel: str
    astTools: list[str]
    file: UploadFile


class AssistantThread(BaseModel):
    astId: str
    threadTitle: str


class AssistantChat(BaseModel):
    astId: str
    threadId: str
    message: str


class AssistantFile(BaseModel):
    fileId: str
    fileName: str
    fileSize: str
    fileType: str
