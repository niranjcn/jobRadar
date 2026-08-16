import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0B1120",
        surface: "#111827",
        elevated: "#172033",
        border: "#263247",
        primary: "#3B82F6",
        accent: "#22D3EE",
        text: {
          DEFAULT: "#F8FAFC",
          secondary: "#94A3B8",
          muted: "#64748B",
        },
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;