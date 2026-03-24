import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import localFont from 'next/font/local';

const inter = localFont({
  src: './font/local/inter.woff2',
  weight: '400',
  style: 'normal',
});


export const metadata: Metadata = {
  title: "AMD Playbooks",
  description: "Find instructions and examples to run AI workloads on AMD hardware — Ryzen™ AI Max, Ryzen™ AI 300, and more",
  icons: {
    icon: "/amd-icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
