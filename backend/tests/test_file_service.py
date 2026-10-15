from pathlib import Path

import pytest

from file_service import FileService


def test_list_notes(tmp_path: Path):
    (tmp_path / "Python.md").write_text(
        "# Python",
        encoding="utf-8",
    )
    (tmp_path / "Algorithms.md").write_text(
        "# Algorithms",
        encoding="utf-8",
    )
    (tmp_path / "ignore.txt").write_text(
        "Not a note",
        encoding="utf-8",
    )

    service = FileService(tmp_path)

    notes = service.list_notes()

    assert len(notes) == 2
    assert {note["title"] for note in notes} == {
        "Python",
        "Algorithms",
    }


def test_create_and_read_note(tmp_path: Path):
    service = FileService(tmp_path)

    note = service.create_note("New Note")

    assert note["title"] == "New Note"
    assert (tmp_path / "New Note.md").exists()


def test_prevent_path_traversal(tmp_path: Path):
    service = FileService(tmp_path)

    with pytest.raises(ValueError):
        service.resolve_note_path("../outside.md")


def test_search_notes(tmp_path: Path):
    (tmp_path / "Python.md").write_text(
        "A language for programming",
        encoding="utf-8",
    )

    service = FileService(tmp_path)

    results = service.search_notes("programming")

    assert len(results) == 1
    assert results[0]["title"] == "Python"
