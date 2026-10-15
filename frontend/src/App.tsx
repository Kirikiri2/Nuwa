import { useMemo, useState } from "react";
import { KnowledgeMap } from "./components/KnowledgeMap";
import { KnowledgeGraph } from "./components/KnowledgeGraph";
import { demoAreas } from "./data/areas";
import type { Area } from "./types/knowledge";
import { NotesPanel } from "./components/NotesPanel";
import { NoteEditor } from "./components/NoteEditor";
import "./App.css";

function App() {
  const [areas, setAreas] = useState<Area[]>(demoAreas);
  const [selectedAreaId, setSelectedAreaId] = useState<string | null>(
    "programming",
  );
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [newAreaTitle, setNewAreaTitle] = useState("");
  const [view, setView] = useState<"map" | "files" | "graph">("map");
  const selectedArea = areas.find(
    (area) => area.id === selectedAreaId,
  );

  const allNotes = useMemo(
    () => areas.flatMap((area) => area.notes),
    [areas],
  );

  const visibleNotes = allNotes.filter((note) =>
    note.title.toLowerCase().includes(search.toLowerCase()),
  );
  const [openedPath, setOpenedPath] = useState<string | null>(null);

  function createArea() {
    const title = newAreaTitle.trim();

    if (!title) return;

    const id = crypto.randomUUID();

    const newArea: Area = {
      id,
      title,
      color: "#D98FB3",
      description: "Новая область знаний",
      points: [
        { x: 160, y: 320 },
        { x: 290, y: 290 },
        { x: 380, y: 345 },
        { x: 355, y: 445 },
        { x: 220, y: 470 },
        { x: 130, y: 405 },
      ],
      notes: [],
    };

    setAreas((current) => [...current, newArea]);
    setSelectedAreaId(id);
    setNewAreaTitle("");
  }

  function addDemoNote() {
    if (!selectedAreaId) return;

    const title = window.prompt("Название заметки");

    if (!title?.trim()) return;

    const id = crypto.randomUUID();

    setAreas((current) =>
      current.map((area) => {
        if (area.id !== selectedAreaId) return area;

        return {
          ...area,
          notes: [
            ...area.notes,
            {
              id,
              title: title.trim(),
              x: 170 + Math.random() * 100,
              y: 160 + Math.random() * 100,
            },
          ],
        };
      }),
    );

    setSelectedNoteId(id);
  }

  const selectedNote = allNotes.find(
    (note) => note.id === selectedNoteId,
  );

  return (
    <div className="app">
      <aside className="sidebar">
        <h1 className="logo">NUWA</h1>
        <p className="subtitle">Your personal knowledge world</p>

        <button
          className={`nav-button ${view === "map" ? "active" : ""}`}
          onClick={() => setView("map")}
        >
          ◈ Карта знаний
        </button>

        <button
          className={`nav-button ${view === "files" ? "active" : ""}`}
          onClick={() => setView("files")}
        >
          ▤ Файлы
        </button>

        <button
          className={`nav-button ${view === "graph" ? "active" : ""}`}
          onClick={() => setView("graph")}
        >
          ⌘ Граф связей
        </button>

        <p className="muted" style={{ marginTop: 32 }}>
          МОИ ОБЛАСТИ
        </p>

        {areas.map((area) => (
          <button
            key={area.id}
            className="nav-button"
            onClick={() => setSelectedAreaId(area.id)}
          >
            <span style={{ color: area.color }}>●</span> {area.title}
          </button>
        ))}
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <h2>Мой мир знаний</h2>
            <p className="muted">
              {areas.length} областей · {allNotes.length} заметок
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() => {
              const title = window.prompt("Название новой области");

              if (title?.trim()) {
                setNewAreaTitle(title);
              }
            }}
          >
            + Создать область
          </button>
        </header>

        {newAreaTitle && (
          <div className="panel editor">
            <label htmlFor="area-title">Название области</label>
            <input
              id="area-title"
              value={newAreaTitle}
              onChange={(event) => setNewAreaTitle(event.target.value)}
            />
            <button className="primary-button" onClick={createArea}>
              Создать
            </button>
          </div>
        )}
        {view === "map" && (
          <KnowledgeMap
            areas={areas}
            selectedAreaId={selectedAreaId}
            onSelectArea={setSelectedAreaId}
            onSelectNote={setSelectedNoteId}
          />
        )}

        {view === "files" && (
          <NotesPanel onOpenNote={setOpenedPath} />
        )}

        {view === "graph" && <KnowledgeGraph />}
        <NotesPanel onOpenNote={setOpenedPath} />

        {openedPath && (
          <NoteEditor
            path={openedPath}
            onClose={() => setOpenedPath(null)}
          />
        )}
        <KnowledgeMap
          areas={areas}
          selectedAreaId={selectedAreaId}
          onSelectArea={setSelectedAreaId}
          onSelectNote={setSelectedNoteId}
        />

        <div className="bottom-grid">
          <section className="panel">
            <h3>
              {selectedArea?.title ?? "Выбери область"}
            </h3>
            <p className="muted">
              {selectedArea?.description ?? "Нажми на страну на карте"}
            </p>

            {selectedArea?.notes.map((note) => (
              <div className="note-row" key={note.id}>
                <button onClick={() => setSelectedNoteId(note.id)}>
                  ◉ {note.title}
                </button>
                <span className="muted">Заметка</span>
              </div>
            ))}

            {selectedArea && (
              <button
                className="primary-button"
                style={{ marginTop: 16 }}
                onClick={addDemoNote}
              >
                + Добавить заметку
              </button>
            )}
          </section>

          <section className="panel">
            <h3>Поиск заметок</h3>
            <input
              className="search-input"
              placeholder="Введите название..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />

            {visibleNotes.map((note) => (
              <div className="note-row" key={note.id}>
                <button onClick={() => setSelectedNoteId(note.id)}>
                  {note.title}
                </button>
              </div>
            ))}

            {selectedNote && (
              <p className="muted">
                Выбрано: {selectedNote.title}
              </p>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;