import json
import sqlite3
from uuid import uuid4

from database import get_connection


def list_areas() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM areas ORDER BY title"
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "color": row["color"],
            "description": row["description"],
            "points": json.loads(row["shape_json"]),
        }
        for row in rows
    ]


def create_area(
    title: str,
    color: str,
    points: list[dict[str, float]],
) -> dict:
    area_id = str(uuid4())

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO areas (id, title, color, shape_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                area_id,
                title,
                color,
                json.dumps(points),
            ),
        )

    return {
        "id": area_id,
        "title": title,
        "color": color,
        "description": "",
        "points": points,
    }


def assign_note(area_id: str, note_id: str) -> None:
    with get_connection() as connection:
        area = connection.execute(
            "SELECT id FROM areas WHERE id = ?",
            (area_id,),
        ).fetchone()

        note = connection.execute(
            "SELECT id FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()

        if area is None or note is None:
            raise ValueError("Область или заметка не найдена")

        connection.execute(
            """
            INSERT OR IGNORE INTO area_notes (area_id, note_id)
            VALUES (?, ?)
            """,
            (area_id, note_id),
        )
