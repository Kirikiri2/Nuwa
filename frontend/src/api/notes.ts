export type NoteFile = {
    path: string;
    title: string;
};

export type NoteDocument = NoteFile & {
    content: string;
};

const API_URL = "http://127.0.0.1:8000/api/v1";

async function request<T>(
    endpoint: string,
    options?: RequestInit,
): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });

    if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `HTTP ${response.status}`);
    }

    return response.json() as Promise<T>;
}

export function connectVault(path: string) {
    return request<{ status: string; notes: NoteFile[] }>("/vaults", {
        method: "POST",
        body: JSON.stringify({ path }),
    });
}

export function fetchNotes() {
    return request<NoteFile[]>("/notes");
}

export function fetchNote(path: string) {
    return request<NoteDocument>(
        `/notes/${path.split("/").map(encodeURIComponent).join("/")}`,
    );
}

export function createNote(title: string) {
    return request<NoteDocument>("/notes", {
        method: "POST",
        body: JSON.stringify({ title }),
    });
}

export function saveNote(path: string, content: string) {
    const encodedPath = path
        .split("/")
        .map(encodeURIComponent)
        .join("/");

    return request<NoteDocument>(`/notes/${encodedPath}`, {
        method: "PUT",
        body: JSON.stringify({ content }),
    });
}

export function searchNotes(query: string) {
    return request<NoteFile[]>(
        `/search?q=${encodeURIComponent(query)}`,
    );
}