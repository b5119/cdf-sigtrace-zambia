import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg"],
      manifest: {
        name: "CDF Pulse — Field Evidence",
        short_name: "CDF Pulse",
        description: "Offline-first field evidence capture for Zambia's CDF projects",
        theme_color: "#0E5C46",
        background_color: "#0B1F1A",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        icons: [
          { src: "icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icon-512.png", sizes: "512x512", type: "image/png" },
        ],
      },
      workbox: {
        // Cache the app shell for offline use; API calls are queued in IndexedDB, not cached
        globPatterns: ["**/*.{js,css,html,svg,woff2}"],
        runtimeCaching: [
          {
            urlPattern: ({ url }) => url.pathname.startsWith("/api/v1/pulse/assignments"),
            handler: "NetworkFirst",
            options: { cacheName: "pulse-assignments", expiration: { maxAgeSeconds: 86400 } },
          },
        ],
      },
      devOptions: { enabled: false },
    }),
  ],
});
