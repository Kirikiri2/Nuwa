import { useState } from "react";
import {
    connectVault,
    createNote,
    fetchNotes,
    type NoteFile,
} from "../api/notes";

type Props = {
    onOpenNote: (path: string) => void;
};

export function NotesPanel({ onOpenNote }: Props) {
    const [vaultPath, setVaultPath] = useState("");
    const [notes, setNotes] = useState<NoteFile[]>([]);
    const [query, setQuery] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    async function refreshNotes() {
        setNotes(await fetchNotes());
    }

    async function handleConnect() {
        setBusy(true);
        setError("");

        try {
            const result = await connectVault(vaultPath);
            setNotes(result.notes);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ошибка подключения");
        } finally {
            setBusy(false);
        }
    }

    async function handleCreate() {
        const title = window.prompt("Название новой заметки");

        if (!title?.trim()) return;

        try {
            const note = await createNote(title.trim());
            await refreshNotes();
            onOpenNote(note.path);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ошибка создания");
        }
    }

    const filteredNotes = notes.filter((note) => {
        const normalizedQuery = query.toLowerCase();

        return (
            note.title.toLowerCase().includes(normalizedQuery) ||
            note.path.toLowerCase().includes(normalizedQuery)
        );
    });

    // useEffect(() => {
    //     if (!vaultPath) return;

    //     // На старте папку подключаем явно кнопкой.
    //     // Автоматический запрос здесь не нужен.
    // }, [vaultPath]);

    return (
        <section className="panel">
            <h3>Файлы Markdown</h3>

            <label htmlFor="vault-path">Путь к папке с заметками</label>

            <input
                id="vault-path"
                className="search-input"
                value={vaultPath}
                onChange={(event) => setVaultPath(event.target.value)}
                placeholder="C:\Users\...\MyNotes"
            />

            <button
                className="primary-button"
                style={{ marginTop: 10 }}
                onClick={handleConnect}
                disabled={busy || !vaultPath.trim()}
            >
                {busy ? "Подключение..." : "Подключить папку"}
            </button>

            {error && <p role="alert">{error}</p>}

            <div className="editor">
                <input
                    className="search-input"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Поиск по названию..."
                />

                <button className="primary-button" onClick={handleCreate}>
                    + Новая заметка
                </button>
            </div>

            {filteredNotes.map((note) => (
                <div className="note-row" key={note.path}>
                    <button onClick={() => onOpenNote(note.path)}>
                        {note.title}
                    </button>
                    <span className="muted">{note.path}</span>
                </div>
            ))}
        </section>
    );
}