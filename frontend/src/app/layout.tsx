import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin", "greek"] })

export const metadata: Metadata = {
  title: "Cyprus Transport Hackaton",
  description: "Digital display system for Cyprus bus stops showing real-time arrivals, ads, and news",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
