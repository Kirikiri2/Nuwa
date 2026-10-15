from pydantic import BaseModel, Field


class VaultRequest(BaseModel):
    path: str = Field(min_length=1, max_length=4096)


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class NoteUpdate(BaseModel):
    content: str = Field(max_length=2_000_000)


class NoteSummary(BaseModel):
    path: str
    title: str


class NoteDetail(NoteSummary):
    content: str
