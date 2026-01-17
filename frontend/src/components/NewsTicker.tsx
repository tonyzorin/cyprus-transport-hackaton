"use client"

import { Newspaper } from "lucide-react"

interface NewsItem {
  id: number
  title: string
  content: string
  source: string | null
}

interface NewsTickerProps {
  news: NewsItem[]
}

export function NewsTicker({ news }: NewsTickerProps) {
  if (news.length === 0) return null

  // Combine all news into a single ticker string
  const tickerText = news
    .map((item) => `${item.title}${item.source ? ` — ${item.source}` : ""}`)
    .join("  •  ")

  return (
    <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white py-2 overflow-hidden">
      <div className="flex items-center">
        <div className="flex-shrink-0 px-3 flex items-center gap-2 border-r border-white/30">
          <Newspaper className="h-4 w-4" />
          <span className="text-sm font-medium">NEWS</span>
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="animate-ticker whitespace-nowrap px-4">
            {tickerText}  •  {tickerText}
          </div>
        </div>
      </div>
    </div>
  )
}
