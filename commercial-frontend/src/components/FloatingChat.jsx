import { useState, useRef, useEffect } from "react";
import { X, Bot, Sparkles, ChevronRight, ArrowRight, BookOpen, Tag, Calendar, Repeat2 } from "lucide-react";
import { sendChatMessage } from "../services/chatService";

const CHIPS = [
  { id: "disponibilidad", label: "Stock", icon: BookOpen, question: "Muéstrame hardware en stock" },
  { id: "precios", label: "Precios", icon: Tag, question: "Muestra productos con precios verificados" },
  { id: "recomendar", label: "Recomendar", icon: Calendar, question: "Recomienda las mejores configuraciones de PC" },
  { id: "alternativas", label: "Alternativas", icon: Repeat2, question: "Estoy buscando alternativas de periféricos" },
];

const SUGGESTIONS = [
  "¿Qué PCs para gaming tienes disponibles?",
  "¿Tienes nuevos monitores para streaming?",
  "Busco una PC para edición y gaming",
];

const SESSION_KEY = "techflow_ai_chat_session_id";

function createSessionId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getInitialSessionId() {
  try {
    const stored = window.localStorage.getItem(SESSION_KEY);
    if (stored) return stored;
    const generated = createSessionId();
    window.localStorage.setItem(SESSION_KEY, generated);
    return generated;
  } catch {
    return createSessionId();
  }
}

export default function FloatingChat() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(getInitialSessionId);
  const [activeChip, setActiveChip] = useState(null);
  const sessionRef = useRef(sessionId);
  const bottomRef = useRef(null);

  useEffect(() => {
    sessionRef.current = sessionId;
    try {
      window.localStorage.setItem(SESSION_KEY, sessionId);
    } catch {
      // No bloquear el chat si localStorage no está disponible.
    }
  }, [sessionId]);

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  async function handleSend(e) {
    e?.preventDefault();
    const question = input.trim();
    if (!question) return;
    sendQuestion(question);
  }

  async function sendQuestion(question) {
    if (loading) return;

    const currentSessionId = sessionRef.current || getInitialSessionId();
    sessionRef.current = currentSessionId;
    setSessionId(currentSessionId);

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(question, currentSessionId);
      if (data?.session_id && data.session_id !== currentSessionId) {
        sessionRef.current = data.session_id;
        setSessionId(data.session_id);
      }
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer || "No recibí respuesta del asistente." }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error al conectar con el asistente." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSuggestion(text) {
    sendQuestion(text);
  }

  function handleChip(chip) {
    setActiveChip((prev) => (prev === chip.id ? null : chip.id));
    sendQuestion(chip.question);
  }

  return (
    <>
      <button className="fcp-trigger" onClick={() => setOpen((o) => !o)} aria-label="Abrir asistente">
        <span className="fcp-trigger__icon">
          <Bot size={18} />
        </span>
        <span className="fcp-trigger__text">
          Asistente IA <strong>PREGÚNTAME</strong>
        </span>
      </button>

      {open && (
        <div className="fcp">
          <div className="fcp__header">
            <span className="fcp__avatar">
              <Bot size={22} />
            </span>
            <div className="fcp__header-info">
              <div className="fcp__header-title-row">
                <span className="fcp__header-title">TechFlow AI</span>
                <span className="fcp__ia-badge">IA</span>
              </div>
              <div className="fcp__header-sub">
                <span className="fcp__dot" />
                Conectado a inventario, precios y soporte técnico
              </div>
            </div>
            <button className="fcp__close" onClick={() => setOpen(false)} aria-label="Cerrar">
              <X size={16} />
            </button>
          </div>

          <div className="fcp__chips">
            {CHIPS.map((chip) => (
              <button
                key={chip.id}
                className={`fcp__chip${activeChip === chip.id ? " fcp__chip--active" : ""}`}
                onClick={() => handleChip(chip)}
              >
                <chip.icon size={12} />
                {chip.label}
              </button>
            ))}
          </div>

          <div className="fcp__messages">
            {messages.length === 0 && (
              <>
                <div className="fcp__msg fcp__msg--ai">
                  <span className="fcp__msg-avatar">
                    <Bot size={14} />
                  </span>
                  <span className="fcp__msg-text">
                    ¡Hola! Puedo ayudarte a encontrar hardware, consultar precios y disponibilidad.
                  </span>
                </div>

                <div className="fcp__suggestions">
                  <span className="fcp__suggestions-label">SUGERENCIAS</span>
                  {SUGGESTIONS.map((s) => (
                    <button key={s} className="fcp__suggestion" onClick={() => handleSuggestion(s)}>
                      <ChevronRight size={13} />
                      {s}
                    </button>
                  ))}
                </div>
              </>
            )}

            {messages.map((msg, i) => (
              <div key={`${msg.role}-${i}-${msg.text.slice(0, 20)}`} className={`fcp__msg fcp__msg--${msg.role === "user" ? "user" : "ai"}`}>
                {msg.role !== "user" && (
                  <span className="fcp__msg-avatar">
                    <Bot size={14} />
                  </span>
                )}
                <span className="fcp__msg-text">
                  {msg.text.split("\n").map((line, index) => (
                    <span key={index}>{index > 0 && <br />}{line}</span>
                  ))}
                </span>
              </div>
            ))}

            {loading && (
              <div className="fcp__msg fcp__msg--ai">
                <span className="fcp__msg-avatar">
                  <Bot size={14} />
                </span>
                <span className="fcp__msg-text fcp__msg-text--typing">
                  <span />
                  <span />
                  <span />
                </span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form className="fcp__input-row" onSubmit={handleSend}>
            <span className="fcp__input-icon">
              <Sparkles size={14} />
            </span>
            <input
              className="fcp__input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu consulta de hardware..."
              disabled={loading}
            />
            <button className="fcp__send" type="submit" disabled={loading || !input.trim()} aria-label="Enviar">
              <ArrowRight size={16} />
            </button>
          </form>

          <p className="fcp__disclaimer">
            Respuestas generadas por IA · Verifica disponibilidad antes de comprar
          </p>
        </div>
      )}
    </>
  );
}
