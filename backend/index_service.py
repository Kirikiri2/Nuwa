import hashlib
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

from database import get_connection
from file_service import FileService
from markdown_parser import extract_tags, extract_wikilinks


def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def make_note_id(vault_id: str, relative_path: str) -> str:
    identity = f"{vault_id}/{relative_path}"
    return str(uuid5(NAMESPACE_URL, identity))


def sync_vault(vault_id: str, service: FileService) -> dict:
    """Обновляет индекс заметок из выбранной папки."""
    files = service.list_notes()
    seen_paths = set()
    links_to_resolve = []

    with get_connection() as connection:
        for file_info in files:
            relative_path = file_info["path"]
            note = service.read_note(relative_path)
            note_id = make_note_id(vault_id, relative_path)
            content = note["content"]
            content_hash = calculate_hash(content)

            seen_paths.add(relative_path)

            connection.execute(
                """
                INSERT INTO notes (
                    id, vault_id, relative_path, title, content_hash
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(vault_id, relative_path)
                DO UPDATE SET
                    title = excluded.title,
                    content_hash = excluded.content_hash
                """,
                (
                    note_id,
                    vault_id,
                    relative_path,
                    note["title"],
                    content_hash,
                ),
            )

            connection.execute(
                "DELETE FROM note_tags WHERE note_id = ?",
                (note_id,),
            )

            for tag in extract_tags(content):
                connection.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag,),
                )

                tag_id = connection.execute(
                    "SELECT id FROM tags WHERE name = ?",
                    (tag,),
                ).fetchone()["id"]

                connection.execute(
                    """
                    INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                    VALUES (?, ?)
                    """,
                    (note_id, tag_id),
                )

            links_to_resolve.append(
                (note_id, relative_path, extract_wikilinks(content))
            )

        # Находим заметки, удалённые из файловой системы.
        existing = connection.execute(
            "SELECT id, relative_path FROM notes WHERE vault_id = ?",
            (vault_id,),
        ).fetchall()

        for row in existing:
            if row["relative_path"] not in seen_paths:
                connection.execute(
                    "DELETE FROM notes WHERE id = ?",
                    (row["id"],),
                )

        # Пересобираем ссылки для этого хранилища.
        connection.execute(
            """
            DELETE FROM note_links
            WHERE source_id IN (
                SELECT id FROM notes WHERE vault_id = ?
            )
            """,
            (vault_id,),
        )

        notes = connection.execute(
            """
            SELECT id, relative_path, title
            FROM notes
            WHERE vault_id = ?
            """,
            (vault_id,),
        ).fetchall()

        by_path = {}
        by_title = {}

        for row in notes:
            by_path[row["relative_path"].casefold()] = row["id"]
            by_title.setdefault(row["title"].casefold(), []).append(row["id"])

        for source_id, source_path, targets in links_to_resolve:
            for target in targets:
                target_path = target.replace("\\", "/").casefold()
                target_id = by_path.get(target_path)

                if target_id is None and "/" not in target:
                    matches = by_title.get(target.casefold(), [])
                    if len(matches) == 1:
                        target_id = matches[0]

                if target_id is not None:
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO note_links (
                            source_id, target_id, link_type
                        )
                        VALUES (?, ?, 'wikilink')
                        """,
                        (source_id, target_id),
                    )

    return {
        "status": "synced",
        "notes_count": len(files),
    }
