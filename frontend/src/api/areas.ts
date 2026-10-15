export type MapPoint = {
    x: number;
    y: number;
};

export type MapArea = {
    id: string;
    title: string;
    color: string;
    description: string;
    points: MapPoint[];
};

const API_URL = "http://127.0.0.1:8000/api/v1";

export async function fetchAreas(): Promise<MapArea[]> {
    const response = await fetch(`${API_URL}/areas`);

    if (!response.ok) {
        throw new Error("Не удалось загрузить области");
    }

    return response.json() as Promise<MapArea[]>;
}