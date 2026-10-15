from pathlib import Path
from uuid import uuid4


class FileService:
    def __init__(self, root: Path):
        self.root = root.resolve()

        if not self.root.is_dir():
            raise ValueError("Папка хранилища не существует")

    def resolve_note_path(self, relative_path: str) -> Path:
        requested = Path(relative_path)

        if requested.is_absolute():
            raise ValueError("Нужен относительный путь")

        if requested.suffix.lower() != ".md":
            raise ValueError("Поддерживаются только .md файлы")

        candidate = (self.root / requested).resolve()

        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Путь выходит за пределы хранилища") from exc

        return candidate

    def list_notes(self) -> list[dict]:
        result = []

        for path in self.root.rglob("*"):
            if not path.is_file() or path.suffix.lower() != ".md":
                continue

            try:
                resolved = path.resolve()
                resolved.relative_to(self.root)
            except (ValueError, OSError):
                continue

            relative_path = resolved.relative_to(self.root).as_posix()

            result.append(
                {
                    "path": relative_path,
                    "title": resolved.stem,
                }
            )

        return sorted(result, key=lambda note: note["title"].lower())

    def read_note(self, relative_path: str) -> dict:
        path = self.resolve_note_path(relative_path)

        if not path.is_file():
            raise FileNotFoundError("Заметка не найдена")

        return {
            "path": relative_path,
            "title": path.stem,
            "content": path.read_text(encoding="utf-8"),
        }

    def create_note(self, title: str) -> dict:
        safe_title = title.strip()

        if (
            not safe_title
            or safe_title in {".", ".."}
            or "/" in safe_title
            or "\\" in safe_title
            or any(ord(char) < 32 for char in safe_title)
        ):
            raise ValueError("Недопустимое название заметки")

        path = self.resolve_note_path(f"{safe_title}.md")
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("x", encoding="utf-8") as file:
            file.write(f"# {safe_title}\n\n")

        return self.read_note(path.relative_to(self.root).as_posix())

    def write_note(self, relative_path: str, content: str) -> dict:
        path = self.resolve_note_path(relative_path)

        if not path.is_file():
            raise FileNotFoundError("Заметка не найдена")

        temp_path = path.with_name(f".{uuid4().hex}.tmp")

        try:
            temp_path.write_text(content, encoding="utf-8")
            temp_path.replace(path)
        finally:
            temp_path.unlink(missing_ok=True)

        return self.read_note(relative_path)

    def search_notes(self, query: str) -> list[dict]:
        normalized_query = query.casefold().strip()

        if not normalized_query:
            return self.list_notes()

        result = []

        for note in self.list_notes():
            content = self.read_note(note["path"])["content"]

            if (
                normalized_query in note["title"].casefold()
                or normalized_query in content.casefold()
            ):
                result.append(note)

        return result
