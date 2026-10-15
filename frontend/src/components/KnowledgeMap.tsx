import type { Area } from "../types/knowledge";

type Props = {
    areas: Area[];
    selectedAreaId: string | null;
    onSelectArea: (id: string) => void;
    onSelectNote: (id: string) => void;
};

export function KnowledgeMap({
    areas,
    selectedAreaId,
    onSelectArea,
    onSelectNote,
}: Props) {
    return (
        <div className="map-viewport">
            <svg
                className="knowledge-map"
                viewBox="0 0 720 540"
                role="img"
                aria-label="Карта знаний Nuwa"
            >
                <defs>
                    <pattern
                        id="map-grid"
                        width="24"
                        height="24"
                        patternUnits="userSpaceOnUse"
                    >
                        <circle cx="1" cy="1" r="1" fill="#343747" />
                    </pattern>
                </defs>

                <rect width="720" height="540" fill="url(#map-grid)" />

                {areas.map((area) => {
                    const selected = selectedAreaId === area.id;
                    const polygonPoints = area.points
                        .map((point) => `${point.x},${point.y}`)
                        .join(" ");
                    return (
                        <g key={area.id}>
                            <polygon
                                points={polygonPoints}
                                fill={area.color}
                                fillOpacity={selected ? 0.42 : 0.2}
                                stroke={area.color}
                                strokeWidth={selected ? 3 : 1.5}
                                onClick={() => onSelectArea(area.id)}
                                className="area-shape"
                            />

                            <text
                                x={area.notes[0]?.x ?? 100}
                                y={(area.notes[0]?.y ?? 100) - 45}
                                fill="#F0F1F7"
                                fontSize="17"
                                fontWeight="600"
                                textAnchor="middle"
                                pointerEvents="none"
                            >
                                {area.title}
                            </text>

                            {area.notes.map((note) => (
                                <g
                                    key={note.id}
                                    className="map-note"
                                    onClick={(event) => {
                                        event.stopPropagation();
                                        onSelectNote(note.id);
                                    }}
                                    role="button"
                                    tabIndex={0}
                                    aria-label={`Открыть заметку ${note.title}`}
                                    onKeyDown={(event) => {
                                        if (event.key === "Enter") {
                                            onSelectNote(note.id);
                                        }
                                    }}
                                >
                                    <circle
                                        cx={note.x}
                                        cy={note.y}
                                        r="8"
                                        fill={area.color}
                                        stroke="#171923"
                                        strokeWidth="3"
                                    />
                                    <text
                                        x={note.x}
                                        y={note.y + 24}
                                        textAnchor="middle"
                                        fill="#E6E7F0"
                                        fontSize="12"
                                        pointerEvents="none"
                                    >
                                        {note.title}
                                    </text>
                                    <circle
                                        cx={note.x}
                                        cy={note.y}
                                        r="15"
                                        fill="transparent"
                                    />
                                </g>
                            ))}
                        </g>
                    );
                })}
            </svg>
        </div>
    );
}