// チャット画面のルートコンポーネント
import { useEffect, useMemo, useRef, useState } from "react";
import { askChat, fetchHistory, editAndRegenerate, deleteHistory, type HistoryItem } from "./api";

const POLL_MS = 5000;

export default function App() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const composingRef = useRef(false); // 文字入力変換中フラグ
  const sendingRef = useRef(false); // 送信中フラグ

  // 履歴を新しい順で表示
  const display = useMemo(() => [...history].reverse(), [history]);
  const topRef = useRef<HTMLDivElement>(null);
  const inFlightRef = useRef(false);
  const pollTimerRef = useRef<number | null>(null);

  // 履歴を取得
  async function loadHistory() {
    const h = await fetchHistory(30);
    setHistory(h);
  }

  // 履歴取得（重複防止）
  async function safeLoadHistory() {
    if (inFlightRef.current) return;
    inFlightRef.current = true;
    try {
      const server = await fetchHistory(30);
      setHistory(prev => {
        const hasOptimistic = prev.some(m => m.id < 0);
        if (server.length === 0 && hasOptimistic) return prev;
        return server;
      });
    } catch (e: any) {
      setErr((e && e.message) || "failed to fetch history");
    } finally {
      inFlightRef.current = false;
    }
  }

  // 初回取得・ポーリング管理
  useEffect(() => {
    safeLoadHistory();
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
    const onVis = () => (document.hidden ? stop() : start());
    document.addEventListener("visibilitychange", onVis);
    return () => {
      stop();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  // メッセージ送信
  async function onSend() {
    const msg = input.trim();
    if (!msg) return;
    if (sendingRef.current) return;
    sendingRef.current = true;
    setErr(null);
    setLoading(true);
    const now = new Date().toISOString();
    const tmpUserId = -Date.now(); // 一時的なID（負の値）
    const tmpAiId = tmpUserId - 1;
    setHistory(prev => [
      ...prev,
      { id: tmpUserId, role: "user", text: msg, ts: now },
      { id: tmpAiId, role: "assistant", text: "（AIが応答中…）", ts: now }
    ]);
    try {
      const res = await askChat(msg);
      setHistory(prev => 
        prev.map(h => (h.id === tmpAiId ? { ...h, text: res.reply } : h))
      );
      setInput("");
      await safeLoadHistory();
    } catch (e: any) {
      setHistory(prev =>
        prev.map(h => (h.id === tmpAiId ? { ...h, text: "（エラーで応答できませんでした）" } : h))
      );
      setErr(e.message || "failed");
    } finally {
      setLoading(false);
      sendingRef.current = false;
      topRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }

  // 編集開始
  async function onStartEdit(item: HistoryItem) {
    setEditId(item.id);
    setEditText(item.text);
  }

  // 編集保存＆再生成
  async function onSaveEdit() {
    if (!editId) return;
    try {
      await editAndRegenerate(editId, editText);
      setEditId(null);
      setEditText("");
      await safeLoadHistory();
    } catch (e:any) {
      setErr(e.message || "update/regenerate failed");
    }
  }
  
  return (
    <div style={{ maxWidth: 800, margin: "24px auto", fontFamily: "system-ui" }}>
      <div ref={topRef} />
      <h1>CB Codecheck Chat</h1>

      <div style={{ display: "flex", gap: 8, position: "sticky", top: 0, background: "white", paddingBottom: 8 }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="メッセージを入力"
          style={{ flex: 1, padding: 8 }}
          onCompositionStart={() => { composingRef.current = true; }}
          onCompositionEnd={() => { composingRef.current = false; }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              const ne = e.nativeEvent as any;
              const composing = composingRef.current || ne?.isComposing || (e as any).keyCode === 229;
              if (composing || e.repeat || sendingRef.current || loading) {
                e.preventDefault();
                return;
              }
              e.preventDefault();
              onSend();
          }}}
        />
        <button onClick={onSend} disabled={!input || loading}>送信</button>
        <button
          onClick={async () => {
            // TODO: リセットボタン押下時の履歴削除処理を実装してください。
            // --- ガイド ---
            // 1. confirmで本当に削除するか確認します。
            // 2. deleteHistory()を呼び出して履歴を削除します。
            // 3. safeLoadHistory()で最新状態を取得します。
            // 4. エラー時はsetErrでエラーメッセージを表示します。
            // 5. loading中はボタンを無効化してください。
          }}
          disabled={loading}
        >
          リセット
        </button>
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
            {m.role === "user" && (
              editId === m.id ? (
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
              )
            )}
            {m.role === "assistant" && (
              <span style={{ whiteSpace: "pre-wrap", flex: 1 }}>{m.text}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
