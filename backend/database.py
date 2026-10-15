import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "nuwa.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS vaults (
                id TEXT PRIMARY KEY,
                root_path TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id TEXT PRIMARY KEY,
                vault_id TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                title TEXT NOT NULL,
                content_hash TEXT,
                FOREIGN KEY (vault_id)
                    REFERENCES vaults(id) ON DELETE CASCADE,
                UNIQUE (vault_id, relative_path)
            );

            CREATE TABLE IF NOT EXISTS areas (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                color TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                shape_json TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS area_notes (
                area_id TEXT NOT NULL,
                note_id TEXT NOT NULL,
                PRIMARY KEY (area_id, note_id),
                FOREIGN KEY (area_id)
                    REFERENCES areas(id) ON DELETE CASCADE,
                FOREIGN KEY (note_id)
                    REFERENCES notes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS note_positions (
                note_id TEXT PRIMARY KEY,
                x REAL NOT NULL,
                y REAL NOT NULL,
                FOREIGN KEY (note_id)
                    REFERENCES notes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS note_links (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                link_type TEXT NOT NULL DEFAULT 'wikilink',
                PRIMARY KEY (source_id, target_id, link_type),
                FOREIGN KEY (source_id)
                    REFERENCES notes(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id)
                    REFERENCES notes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS map_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS note_tags (
                note_id TEXT NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id)
                    REFERENCES notes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id)
                    REFERENCES tags(id) ON DELETE CASCADE
            );
            """
        )
