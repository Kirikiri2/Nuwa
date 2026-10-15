import { useEffect, useState } from "react";
import { fetchNote, saveNote } from "../api/notes";

type Props = {
    path: string;
    onClose: () => void;
};

export function NoteEditor({ path, onClose }: Props) {
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");
    const [error, setError] = useState("");
    const [status, setStatus] = useState("");

    useEffect(() => {
        let cancelled = false;

        fetchNote(path)
            .then((note) => {
                if (cancelled) return;

                setTitle(note.title);
                setContent(note.content);
            })
            .catch((err: unknown) => {
                if (cancelled) return;

                setError(
                    err instanceof Error ? err.message : "Не удалось открыть файл",
                );
            });

        return () => {
            cancelled = true;
        };
    }, [path]);

    async function handleSave() {
        setError("");
        setStatus("");

        try {
            await saveNote(path, content);
            setStatus("Сохранено");
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "Не удалось сохранить",
            );
        }
    }

    return (
        <section className="panel editor">
            <div className="topbar">
                <div>
                    <h3>{title || "Открытие заметки..."}</h3>
                    <p className="muted">{path}</p>
                </div>

                <button onClick={onClose}>Закрыть</button>
            </div>

            {error && <p role="alert">{error}</p>}

            <textarea
                value={content}
                onChange={(event) => {
                    setContent(event.target.value);
                    setStatus("Есть несохранённые изменения");
                }}
                aria-label="Содержимое Markdown-файла"
            />

            <div className="topbar">
                <span className="muted">{status}</span>
                <button className="primary-button" onClick={handleSave}>
                    Сохранить
                </button>
            </div>
        </section>
    );
}