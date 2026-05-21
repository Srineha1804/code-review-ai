import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Code Review AI",
  description: "AI-powered bug detection for your pull requests",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
