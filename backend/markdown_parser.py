import re

WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
TAG_PATTERN = re.compile(r"(?<!\w)#([\w/-]+)", re.UNICODE)


def extract_wikilinks(content: str) -> list[str]:
    """Извлекает названия заметок из ссылок Obsidian."""
    links = []

    for match in WIKILINK_PATTERN.findall(content):
        target = match.split("|", maxsplit=1)[0]
        target = target.split("#", maxsplit=1)[0]
        target = target.strip()

        if target:
            links.append(target)

    return list(dict.fromkeys(links))


def extract_tags(content: str) -> list[str]:
    """Извлекает уникальные теги из текста."""
    return list(dict.fromkeys(TAG_PATTERN.findall(content)))
