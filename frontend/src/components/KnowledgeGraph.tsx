import { useEffect, useState } from "react";
import {
    Background,
    Controls,
    ReactFlow,
    type Edge,
    type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type GraphResponse = {
    nodes: { id: string; title: string }[];
    edges: { source: string; target: string }[];
};

export function KnowledgeGraph() {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        let cancelled = false;

        fetch("http://127.0.0.1:8000/api/v1/graph")
            .then(async (response) => {
                if (!response.ok) {
                    throw new Error("Сначала подключите хранилище");
                }

                return (await response.json()) as GraphResponse;
            })
            .then((data) => {
                if (cancelled) return;

                setNodes(
                    data.nodes.map((note, index) => ({
                        id: note.id,
                        position: {
                            x: (index % 4) * 220,
                            y: Math.floor(index / 4) * 120,
                        },
                        data: { label: note.title },
                    })),
                );

                setEdges(
                    data.edges.map((edge, index) => ({
                        id: `edge-${index}`,
                        source: edge.source,
                        target: edge.target,
                        animated: false,
                    })),
                );
            })
            .catch((err: unknown) => {
                if (!cancelled) {
                    setError(
                        err instanceof Error ? err.message : "Ошибка загрузки графа",
                    );
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    if (error) return <p role="alert">{error}</p>;

    return (
        <div style={{ width: "100%", height: 600 }}>
            <ReactFlow nodes={nodes} edges={edges} fitView>
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
}