import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Mono, Inter } from "next/font/google";
import { TelegramBridge } from "@/components/telegram-bridge";
import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

// Privacy (GDPR): next/font/google is SELF-HOSTED — font files are downloaded
// once at build time and served from /_next/static. The browser never contacts
// fonts.googleapis.com / fonts.gstatic.com, so no visitor IP leaks to Google.
// Do NOT add <link> tags to Google Fonts or any CDN-hosted fonts; keep all
// fonts served from this origin (guarded by test/legal-guards.test.ts).

const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["700", "800"],
  variable: "--font-fraunces",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-plex",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// Keep JetBrains for compatibility (mono fallback)
import { JetBrains_Mono } from "next/font/google";
const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "JobQuest",
  description: "Your radar for the job market.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      data-theme="warm"
      className={`${fraunces.variable} ${plexMono.variable} ${inter.variable} ${jetbrains.variable}`}
    >
      <body className="min-h-screen font-sans">
        <AuthProvider>
          <TelegramBridge />
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}