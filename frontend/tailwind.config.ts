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
        bg: "rgb(var(--color-bg) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        elevated: "rgb(var(--color-elevated) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        primary: "rgb(var(--color-primary) / <alpha-value>)",
        accent: "rgb(var(--color-accent) / <alpha-value>)",
        text: {
          DEFAULT: "rgb(var(--color-text) / <alpha-value>)",
          secondary: "rgb(var(--color-text-secondary) / <alpha-value>)",
          muted: "rgb(var(--color-text-muted) / <alpha-value>)",
        },
        success: "rgb(var(--color-success) / <alpha-value>)",
        warning: "rgb(var(--color-warning) / <alpha-value>)",
        danger: "rgb(var(--color-danger) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "-apple-system", "sans-serif"],
        display: ["var(--font-fraunces)", "var(--font-inter)", "serif"],
        mono: ["var(--font-plex)", "var(--font-jetbrains)", "ui-monospace", "monospace"],
        fraunces: ["var(--font-fraunces)", "serif"],
        plex: ["var(--font-plex)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        DEFAULT: "10px",
        sm: "10px",
        md: "14px",
        lg: "20px",
        xl: "24px",
      },
      boxShadow: {
        offset: "var(--shadow-offset)",
        "offset-hover": "var(--shadow-offset-hover)",
        "offset-sm": "var(--shadow-offset-sm)",
        soft: "var(--shadow-soft)",
        // legacy — kept for compat, now alias to offset
        "neo-raised": "var(--shadow-offset)",
        "neo-flat": "var(--shadow-offset-sm)",
        "neo-pressed": "var(--shadow-offset-sm)",
        "neo-hover": "var(--shadow-offset-hover)",
        "neo-glow": "var(--shadow-soft)",
      },
      backdropBlur: {
        glass: "16px",
      },
    },
  },
  plugins: [],
};

export default config;