/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#0E5C46", "primary-h": "#0A4533",
        accent: "#B8762A", "accent-h": "#9C6322", ink: "#0B1F1A",
        surface: "#F6F8F6", "surface-2": "#EEF3EF", card: "#FFFFFF",
        "on-surface": "#191c1b", "on-surface-variant": "#3f4944",
        outline: "#6f7974", "outline-variant": "#D7E0DA",
        "risk-low": "#138636", "risk-mid": "#B45309", "risk-high": "#B91C1C",
        sidebar: "#0B1F1A", "sidebar-2": "#13302A", "sidebar-text": "#E7EFEA", "sidebar-muted": "#8FA89C",
        info: "#1D4ED8",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
}
