const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export type HistoryItem = { id:number; role:"user"|"assistant"; text:string; ts:string };
export type AskResponse = { reply:string; tokens_input?:number; tokens_output?:number };

export async function askChat(message: string, system?: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/chat/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, system })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({} as any));
    if (res.status === 429) throw new Error("混み合っています。少し待って再実行してください。");
    if (res.status === 502) throw new Error("上流APIでエラーが発生しました。時間をおいて再試行してください。");
    throw new Error(err?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchHistory(limit=20): Promise<HistoryItem[]> {
  const r = await fetch(`${API_BASE}/api/chat/history?limit=${limit}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function updateMessage(id:number, text:string): Promise<HistoryItem> {
  const r = await fetch(`${API_BASE}/api/chat/message/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  if (!r.ok) {
    const e = await r.json().catch(()=>({}));
    throw new Error(e?.detail || `HTTP ${r.status}`);
  }
  return r.json();
}

export async function deleteHistory(): Promise<void> {
  const r = await fetch(`${API_BASE}/api/chat/history`, { method: "DELETE" });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
}