# pulse-pwa — CDF Pulse field app (React + Vite + TS + Workbox)

Offline-first installable PWA for community monitors and institutional confirmers. Screens M1–M8
(see `../../docs/04_SCREENS.md`). Built in **INC-010** (capture + offline sync) and **INC-013**
(confirmation inbox).

Key pieces:
- **Capture:** camera + automatic GPS lock + timestamp embedded at capture time.
- **Offline:** service worker + IndexedDB queue; submissions created offline and synced on reconnect
  with an `Idempotency-Key` for exactly-once delivery.
- **Sync status** UI; **confirmation inbox** for `inst_confirmer`.
- Photos go to IPFS via the backend (INC-011); confirmations hit the Polygon contract (INC-012/013).

Accessibility + low-bandwidth first (small assets, works on mid-range Android).
