"use client";

import { useEffect } from "react";

type TelegramWebApp = {
  ready: () => void;
  expand: () => void;
  disableVerticalSwipes?: () => void;
  themeParams?: Record<string, string>;
  colorScheme?: string;
  setHeaderColor?: (color: string) => void;
  setBackgroundColor?: (color: string) => void;
  onEvent?: (event: string, cb: () => void) => void;
};

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp };
  }
}

/**
 * Initializes the Telegram Mini App bridge when the dashboard is opened
 * inside Telegram. No-ops in a normal browser (window.Telegram is absent),
 * so the regular web build is unaffected.
 */
export function TelegramBridge() {
  useEffect(() => {
    const webApp = window.Telegram?.WebApp;
    if (!webApp) return;

    // Signal readiness and request a full-height viewport.
    webApp.ready();
    webApp.expand();

    // Match the app theme to Telegram's current theme.
    const theme = webApp.colorScheme === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", theme);

    // Headless chrome: use the theme's background so there's no flash of the
    // default header/background on small screens.
    const bg = webApp.themeParams?.bg_color;
    if (bg) {
      webApp.setHeaderColor?.(bg);
      webApp.setBackgroundColor?.(bg);
    }

    // Prefer a stable, non-swipeable viewport inside Telegram.
    webApp.disableVerticalSwipes?.();
  }, []);

  return null;
}
