import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClaimFlow | Evidence Operations",
  description: "Synthetic-claims evidence and exception review prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
