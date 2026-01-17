import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin", "greek"] })

export const metadata: Metadata = {
  title: "Bus Hackaton - Cyprus Bus Stop Digital Displays",
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
