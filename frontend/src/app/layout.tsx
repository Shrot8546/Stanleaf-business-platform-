import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Stanleaf | Business Intelligence, Simplified.",
  description:
    "Business Health Intelligence platform analyzing public and owner-provided data to benchmark performance, predict trends, and deliver explainable health scores.",
};

export default function RootLayout({
  children,
}: ReadnxProps<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen flex flex-col antialiased bg-slate-50 text-slate-900`}>
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

type ReadnxProps<T> = T;
