import { useState, useRef, useEffect, FormEvent } from "react";
import { Send, Bot, User, Loader2, AlertTriangle } from "lucide-react";
import api from "../services/api";

interface Message {
  role: "user" | "assistant";
  text: string;
  intent?: string;
}

interface ChatApiResponse {
  session_id: string;
  intent: string;
  answer: string;
  interaction_id: string | null;
}

const AsistentePage = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Hola, soy el asistente comercial de TechFlow. Puedes preguntarme sobre disponibilidad de libros, precios, categorías o cualquier consulta del catálogo.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string | undefined>(undefined);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (e: FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setError(null);
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    try {
      const data: ChatApiResponse = await api.post("/chat", {
        question,
        session_id: sessionIdRef.current,
      });
      sessionIdRef.current = data.session_id;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, intent: data.intent },
      ]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error al contactar el asistente";
      setError(msg);
      setMessages((prev) => prev.slice(0, -1));
      setInput(question);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-4">
        <h2 className="font-serif text-[20px] text-[#f1f5f9]">Asistente Comercial IA</h2>
        <p className="text-[12.5px] text-[#64748b]">Consultas sobre catálogo, precios y disponibilidad en tiempo real</p>
      </div>

      {/* Chat window */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-[#1e293b] bg-[#0a0f1e] p-4 scrollbar-clean">
        <div className="flex flex-col gap-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white ${
                  m.role === "assistant" ? "bg-amber-500/80" : "bg-[#3b82f6]"
                }`}
              >
                {m.role === "assistant" ? <Bot size={15} /> : <User size={15} />}
              </div>
              <div className={`max-w-[72%] ${m.role === "user" ? "items-end" : "items-start"} flex flex-col gap-1`}>
                {m.intent && m.role === "assistant" && (
                  <span className="inline-block rounded-full bg-[#1e293b] px-2 py-0.5 text-[10px] text-[#64748b]">
                    {m.intent}
                  </span>
                )}
                <div
                  className={`rounded-xl px-4 py-2.5 text-[13.5px] leading-relaxed whitespace-pre-wrap ${
                    m.role === "assistant"
                      ? "bg-[#1e293b] text-[#e2e8f0]"
                      : "bg-[#3b82f6] text-white"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500/80 text-white">
                <Bot size={15} />
              </div>
              <div className="flex items-center gap-2 rounded-xl bg-[#1e293b] px-4 py-2.5 text-[13.5px] text-[#64748b]">
                <Loader2 size={14} className="animate-spin" />
                <span>Consultando…</span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mt-3 flex items-center gap-2 rounded-lg border border-red-800/50 bg-red-950/40 px-4 py-2.5 text-[13px] text-red-300">
          <AlertTriangle size={14} className="shrink-0" />
          {error}
        </div>
      )}

      {/* Input */}
      <form onSubmit={send} className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Pregunta algo sobre el catálogo, precios o disponibilidad…"
          disabled={loading}
          className="flex-1 rounded-xl border border-[#334155] bg-[#1e293b] px-4 py-2.5 text-[13.5px] text-[#f1f5f9] placeholder:text-[#64748b] outline-none focus:ring-2 focus:ring-[#3b82f6] disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#3b82f6] text-white transition hover:bg-[#2563eb] disabled:opacity-40"
        >
          <Send size={15} />
        </button>
      </form>
    </div>
  );
};

export default AsistentePage;
