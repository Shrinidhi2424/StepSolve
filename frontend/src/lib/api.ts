import { Topic, SolveResponse } from "./types";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getTopics(): Promise<Topic[]> {
  const res = await fetch(`${BACKEND_URL}/api/topics`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch topics: ${res.statusText}`);
  }
  return res.json();
}

export async function getTopic(id: string): Promise<Topic> {
  const res = await fetch(`${BACKEND_URL}/api/topics/${id}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch topic '${id}': ${res.statusText}`);
  }
  return res.json();
}

export async function solve(
  topicId: string,
  payload: Record<string, any>
): Promise<SolveResponse> {
  const res = await fetch(`${BACKEND_URL}/api/solve/${topicId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Solve failed: ${res.statusText}`);
  }
  return data;
}

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${BACKEND_URL}/api/health`);
  if (!res.ok) {
    throw new Error("Backend service unreachable");
  }
  return res.json();
}
