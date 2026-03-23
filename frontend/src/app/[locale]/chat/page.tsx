"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";

interface Message {
  role: "user" | "assistant";
  content: string;
  confidence?: number;
}

export default function ChatPage() {
  const t = useTranslations("ai");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token") || "";
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    const ws = new WebSocket(`${wsUrl}/chat?token=${token}`);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "typing") {
        setThinking(data.status);
      } else if (data.type === "ai_response") {
        setThinking(false);
        setMessages((prev) => [...prev, { role: "assistant", content: data.content, confidence: data.confidence }]);
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  function send() {
    if (!input.trim() || !wsRef.current) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    wsRef.current.send(JSON.stringify({ type: "message", content: input, locale: "fr" }));
    setInput("");
  }

  return (
    <main style={{ padding: 24, maxWidth: 700, margin: "0 auto" }}>
      <h1>{t("sources")}</h1>
      <div style={{ border: "1px solid #ccc", padding: 16, minHeight: 400, marginBottom: 12, overflowY: "auto" }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 8, textAlign: m.role === "user" ? "right" : "left" }}>
            <strong>{m.role === "user" ? "Vous" : "IA"}</strong>
            <p>{m.content}</p>
            {m.confidence !== undefined && m.confidence < 0.6 && <small style={{ color: "orange" }}>{t("lowConfidence")}</small>}
          </div>
        ))}
        {thinking && <p><em>{t("thinking")}</em></p>}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder={t("askQuestion")} style={{ flex: 1, padding: 8 }} />
        <button onClick={send}>↑</button>
      </div>
      <small style={{ color: "gray" }}>{t("disclaimer")}</small>
    </main>
  );
}
