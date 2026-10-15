export type Note = {
    id: string;
    title: string;
    x: number;
    y: number;
};

export type MapPoint = {
    x: number;
    y: number;
};

export type Area = {
    id: string;
    title: string;
    color: string;
    description: string;
    points: MapPoint[];
    notes: Note[];
};