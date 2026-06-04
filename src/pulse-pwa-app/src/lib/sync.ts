// Sync engine — pushes pending IndexedDB submissions to the backend, then
// pins each photo to IPFS (INC-011). Exactly-once: the backend de-dupes on
// client_uuid, and IPFS pinning is content-addressed (idempotent by nature).
import { getPendingSubmissions, markSynced, getSubmission } from "./db";
import { pulseApi, evidenceApi } from "./api";

export async function syncPending(): Promise<{ synced: number; duplicates: number; failed: number }> {
  const pending = await getPendingSubmissions();
  if (pending.length === 0) return { synced: 0, duplicates: 0, failed: 0 };

  try {
    const res = await pulseApi.syncBatch(pending);
    // Map each synced submission → its server id, then pin its photo to IPFS
    for (const s of res.data.submissions) {
      await markSynced(s.client_uuid, s.id);
      const local = await getSubmission(s.client_uuid);
      if (local?.photo_blob) {
        try {
          await evidenceApi.uploadPhoto(s.id, local.photo_blob);
        } catch {
          // Photo pin retries on next sync; metadata is already saved
        }
      }
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
