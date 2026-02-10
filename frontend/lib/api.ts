const API_BASE = "http://127.0.0.1:8000";

export async function apiFetch(
  url: string,
  options: RequestInit = {}
) {
  const token = localStorage.getItem("access");

  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  return res.json();
}
