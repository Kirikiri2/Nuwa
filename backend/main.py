from pathlib import Path

from database import initialize_database

from pydantic import BaseModel, Field

from area_service import assign_note, create_area, list_areas

from uuid import uuid4
from graph_service import get_graph
from database import get_connection
from index_service import sync_vault

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from file_service import FileService
from schemas import NoteCreate, NoteDetail
from schemas import NoteSummary, NoteUpdate, VaultRequest


class AreaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    points: list[dict[str, float]] = Field(min_length=3, max_length=100)


class AssignNoteRequest(BaseModel):
    note_id: str


app = FastAPI(title="Nuwa API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type"],
)

vault: FileService | None = None
vault_id: str | None = None


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/vaults")
def connect_vault(request: VaultRequest):
    global vault, vault_id

    try:
        service = FileService(Path(request.path))
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resolved_path = str(service.root)

    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM vaults WHERE root_path = ?",
            (resolved_path,),
        ).fetchone()

        if row:
            current_vault_id = row["id"]
        else:
            current_vault_id = str(uuid4())

            connection.execute(
                "INSERT INTO vaults (id, root_path) VALUES (?, ?)",
                (current_vault_id, resolved_path),
            )

    try:
        result = sync_vault(current_vault_id, service)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="Не удалось проиндексировать файлы",
        ) from exc

    vault = service
    vault_id = current_vault_id

    return result


@app.post("/api/v1/vaults/sync")
def resync_vault():
    if vault is None or vault_id is None:
        raise HTTPException(
            status_code=400,
            detail="Сначала подключите папку",
        )

    try:
        return sync_vault(vault_id, vault)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="Не удалось синхронизировать файлы",
        ) from exc


def get_vault() -> FileService:
    if vault is None:
        raise HTTPException(
            status_code=400,
            detail="Сначала подключите папку с заметками",
        )

    return vault


@app.get("/api/v1/notes", response_model=list[NoteSummary])
def list_notes():
    return get_vault().list_notes()


@app.get("/api/v1/notes/{relative_path:path}", response_model=NoteDetail)
def read_note(relative_path: str):
    try:
        return get_vault().read_note(relative_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/notes", response_model=NoteDetail)
def create_note(request: NoteCreate):
    try:
        return get_vault().create_note(request.title)
    except FileExistsError as exc:
        raise HTTPException(
            status_code=409,
            detail="Заметка с таким названием уже существует",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/api/v1/notes/{relative_path:path}", response_model=NoteDetail)
def update_note(relative_path: str, request: NoteUpdate):
    try:
        return get_vault().write_note(relative_path, request.content)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/v1/search", response_model=list[NoteSummary])
def search_notes(q: str = ""):
    return get_vault().search_notes(q)


@app.get("/api/v1/areas")
def get_areas():
    return list_areas()


@app.post("/api/v1/areas")
def post_area(request: AreaCreate):
    return create_area(
        request.title,
        request.color,
        request.points,
    )


@app.post("/api/v1/areas/{area_id}/notes")
def post_assign_note(area_id: str, request: AssignNoteRequest):
    try:
        assign_note(area_id, request.note_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"status": "assigned"}


@app.get("/api/v1/graph")
def graph():
    if vault_id is None:
        raise HTTPException(
            status_code=400,
            detail="Сначала подключите папку",
        )

    return get_graph(vault_id)
