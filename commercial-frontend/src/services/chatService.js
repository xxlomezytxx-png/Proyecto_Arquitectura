const BFF_URL = import.meta.env.VITE_BFF_URL || "http://localhost:8009";

export async function sendChatMessage(question, sessionId = null) {
  const resp = await fetch(`${BFF_URL}/api/assistant/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
  if (!resp.ok) {
    throw new Error(`Chat error: ${resp.status}`);
  }
  return resp.json();
}
