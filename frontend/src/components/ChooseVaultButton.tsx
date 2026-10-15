import { useState } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { connectVault } from "../api/notes";

type Props = {
    onConnected: () => void;
};

export function ChooseVaultButton({ onConnected }: Props) {
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");

    async function chooseFolder() {
        setError("");

        try {
            const selected = await open({
                directory: true,
                multiple: false,
                title: "Выбери папку с Markdown-заметками",
            });

            if (typeof selected !== "string") return;

            setBusy(true);

            await connectVault(selected);
            onConnected();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Не удалось подключить папку",
            );
        } finally {
            setBusy(false);
        }
    }

    return (
        <div>
            <button
                className="primary-button"
                onClick={chooseFolder}
                disabled={busy}
            >
                {busy ? "Подключение..." : "Выбрать папку"}
            </button>

            {error && <p role="alert">{error}</p>}
        </div>
    );
}