import { useEffect, useMemo, useRef, useState } from "react";
import { askChat, fetchHistory, updateMessage, type HistoryItem } from "./api";

const POLL_MS = 5000; // 自動更新間隔（ミリ秒）

export default function App() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [editText, setEditText] = useState("");

  // 最新→古い順で上から表示
  const display = useMemo(() => [...history].reverse(), [history]);
  const topRef = useRef<HTMLDivElement>(null);

  // 重複ポーリング防止
  const inFlightRef = useRef(false);
  const pollTimerRef = useRef<number | null>(null);

  async function loadHistory() {
    const h = await fetchHistory(30);
    setHistory(h);
  }

  async function safeLoadHistory() {
    if (inFlightRef.current) return;
    inFlightRef.current = true;
    try {
      await loadHistory();
    } catch (e: any) {
      setErr((e && e.message) || "failed to fetch history");
    } finally {
      inFlightRef.current = false;
    }
  }

  useEffect(() => {
    // 初回取得
    safeLoadHistory();

    // ポーリング開始/停止
    const start = () => {
      if (pollTimerRef.current != null) return;
      pollTimerRef.current = window.setInterval(safeLoadHistory, POLL_MS);
    };
    const stop = () => {
      if (pollTimerRef.current != null) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };

    start();

    // タブ非表示時は停止、復帰で再開（節約）
    const onVis = () => (document.hidden ? stop() : start());
    document.addEventListener("visibilitychange", onVis);

    return () => {
      stop();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  async function onSend() {
    const msg = input.trim();
    if (!msg) return;
    setErr(null);
    setLoading(true);
    try {
      await askChat(msg);
      setInput("");
      await safeLoadHistory(); // 送信直後も最新化
    } catch (e: any) {
      setErr(e.message || "failed");
    } finally {
      setLoading(false);
      topRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }

  async function onStartEdit(item: HistoryItem) {
    setEditId(item.id);
    setEditText(item.text);
  }

  async function onSaveEdit() {
    if (!editId) return;
    try {
      await updateMessage(editId, editText);
      setEditId(null);
      setEditText("");
      await safeLoadHistory();
    } catch (e: any) {
      setErr(e.message || "update failed");
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: "24px auto", fontFamily: "system-ui" }}>
      <div ref={topRef} />
      <h1>CB Codecheck Chat</h1>

      <div style={{ display: "flex", gap: 8, position: "sticky", top: 0, background: "white", paddingBottom: 8 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="メッセージを入力"
          style={{ flex: 1, padding: 8 }}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && onSend()}
        />
        <button onClick={onSend} disabled={!input || loading}>送信</button>
        {/* 手動の「更新」ボタンは削除しました */}
      </div>

      {loading && <p>待機中…</p>}
      {err && <p style={{ color: "crimson" }}>エラー: {err}</p>}

      <div style={{ marginTop: 12, display: "grid", gap: 8, maxHeight: "70vh", overflowY: "auto", borderTop: "1px solid #eee", paddingTop: 8 }}>
        {display.map((m) => (
          <div key={m.id} style={{
            border: "1px solid #e5e7eb",
            padding: 10, borderRadius: 8,
            background: m.role === "assistant" ? "#f8fafc" : "white",
            display: "flex", gap: 8, alignItems: "center"
          }}>
            <strong style={{ width: 80 }}>{m.role === "assistant" ? "AI" : "You"}</strong>
            {editId === m.id ? (
              <>
                <input value={editText} onChange={e=>setEditText(e.target.value)} style={{ flex: 1, padding: 6 }}/>
                <button onClick={onSaveEdit}>保存</button>
                <button onClick={()=>{setEditId(null); setEditText("");}}>取消</button>
              </>
            ) : (
              <>
                <span style={{ whiteSpace: "pre-wrap", flex: 1 }}>{m.text}</span>
                <button onClick={() => onStartEdit(m)} title="このメッセージを更新">編集</button>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
