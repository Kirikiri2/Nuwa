from database import get_connection


def get_graph(vault_id: str) -> dict:
    with get_connection() as connection:
        notes = connection.execute(
            """
            SELECT id, title
            FROM notes
            WHERE vault_id = ?
            """,
            (vault_id,),
        ).fetchall()

        links = connection.execute(
            """
            SELECT nl.source_id, nl.target_id
            FROM note_links AS nl
            JOIN notes AS source ON source.id = nl.source_id
            JOIN notes AS target ON target.id = nl.target_id
            WHERE source.vault_id = ?
              AND target.vault_id = ?
            """,
            (vault_id, vault_id),
        ).fetchall()

    return {
        "nodes": [
            {
                "id": row["id"],
                "title": row["title"],
            }
            for row in notes
        ],
        "edges": [
            {
                "source": row["source_id"],
                "target": row["target_id"],
            }
            for row in links
        ],
    }
