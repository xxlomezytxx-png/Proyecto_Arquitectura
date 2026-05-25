const BFF_URL = import.meta.env.VITE_BFF_URL || "http://localhost:8000";

export async function getRecommendations(bookId) {
  const resp = await fetch(`${BFF_URL}/api/recommendations/${bookId}`);
  if (!resp.ok) {
    return [];
  }
  return resp.json();
}
