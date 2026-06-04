// Sync engine — pushes pending IndexedDB submissions to the backend.
// Exactly-once: the backend de-dupes on client_uuid, so retries are safe.
import { getPendingSubmissions, markSynced } from "./db";
import { pulseApi } from "./api";

export async function syncPending(): Promise<{ synced: number; duplicates: number; failed: number }> {
  const pending = await getPendingSubmissions();
  if (pending.length === 0) return { synced: 0, duplicates: 0, failed: 0 };

  try {
    const res = await pulseApi.syncBatch(pending);
    // Mark each synced by matching client_uuid → server id
    for (const s of res.data.submissions) {
      await markSynced(s.client_uuid, s.id);
    }
    return { synced: res.data.synced, duplicates: res.data.duplicates, failed: 0 };
  } catch {
    return { synced: 0, duplicates: 0, failed: pending.length };
  }
}

export function onReconnect(callback: () => void): () => void {
  window.addEventListener("online", callback);
  return () => window.removeEventListener("online", callback);
}
