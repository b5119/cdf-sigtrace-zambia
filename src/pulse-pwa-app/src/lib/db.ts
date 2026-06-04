// IndexedDB offline queue for Pulse submissions.
// Every captured submission lands here first (works fully offline),
// then syncs to the backend when connectivity returns. Exactly-once
// is guaranteed by the client_uuid which the backend de-dupes on.
import { openDB, type DBSchema, type IDBPDatabase } from "idb";

export interface QueuedSubmission {
  client_uuid: string;          // primary key — also the idempotency key
  project_id: string;
  constituency_id?: string;
  lat: number;
  lng: number;
  category?: string;
  note?: string;
  captured_at: string;          // ISO device timestamp
  photo_blob?: Blob;            // local photo (uploaded to IPFS at INC-011)
  sync_status: "pending" | "synced" | "error";
  server_id?: string;           // assigned after sync
  created_at: string;
}

interface PulseDB extends DBSchema {
  submissions: {
    key: string;                // client_uuid
    value: QueuedSubmission;
    indexes: { "by-status": string };
  };
}

let _db: Promise<IDBPDatabase<PulseDB>> | null = null;

function getDb() {
  if (!_db) {
    _db = openDB<PulseDB>("cdf-pulse", 1, {
      upgrade(db) {
        const store = db.createObjectStore("submissions", { keyPath: "client_uuid" });
        store.createIndex("by-status", "sync_status");
      },
    });
  }
  return _db;
}

export async function queueSubmission(sub: QueuedSubmission): Promise<void> {
  const db = await getDb();
  await db.put("submissions", sub);
}

export async function getAllSubmissions(): Promise<QueuedSubmission[]> {
  const db = await getDb();
  const all = await db.getAll("submissions");
  return all.sort((a, b) => b.created_at.localeCompare(a.created_at));
}

export async function getPendingSubmissions(): Promise<QueuedSubmission[]> {
  const db = await getDb();
  return db.getAllFromIndex("submissions", "by-status", "pending");
}

export async function markSynced(client_uuid: string, server_id: string): Promise<void> {
  const db = await getDb();
  const sub = await db.get("submissions", client_uuid);
  if (sub) {
    sub.sync_status = "synced";
    sub.server_id = server_id;
    await db.put("submissions", sub);
  }
}

export async function getSubmission(client_uuid: string): Promise<QueuedSubmission | undefined> {
  const db = await getDb();
  return db.get("submissions", client_uuid);
}

export function newClientUuid(): string {
  // RFC4122-ish unique id, > 8 chars (backend requires min 8)
  return "cu-" + crypto.randomUUID();
}
