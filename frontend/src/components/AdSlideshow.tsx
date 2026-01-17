"use client"

import { useState, useEffect, useRef } from "react"
import { Image as ImageIcon, Newspaper } from "lucide-react"
import { API_URL } from "@/lib/utils"

interface Ad {
  id: number
  title: string
  image_url: string
  link_url: string | null
  advertiser_name: string | null
  duration_seconds: number
}

interface NewsItem {
  id: number
  title_el: string
  content_el: string
  title_en: string | null
  content_en: string | null
  image_url: string | null
  source: string | null
  duration_seconds: number
}

// Union type for slideshow items
type SlideItem = 
  | { type: "ad"; data: Ad }
  | { type: "news"; data: NewsItem }

interface AdSlideshowProps {
  ads: Ad[]
  news?: NewsItem[]
  defaultDuration?: number
}

export function AdSlideshow({ ads, news = [], defaultDuration = 10 }: AdSlideshowProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [progress, setProgress] = useState(0)
  const progressRef = useRef<NodeJS.Timeout | null>(null)
  const slideRef = useRef<NodeJS.Timeout | null>(null)

  // Combine ads and news into a single slideshow
  const slides: SlideItem[] = [
    ...ads.map((ad): SlideItem => ({ type: "ad", data: ad })),
    ...news.map((item): SlideItem => ({ type: "news", data: item })),
  ]

  // Get duration for current slide
  const getCurrentDuration = () => {
    if (slides.length === 0) return defaultDuration
    const currentSlide = slides[currentIndex]
    if (currentSlide.type === "ad") {
      return currentSlide.data.duration_seconds || defaultDuration
    } else {
      return currentSlide.data.duration_seconds || 12
    }
  }

  useEffect(() => {
    if (slides.length <= 0) return

    const duration = getCurrentDuration() * 1000
    const progressInterval = 50 // Update progress every 50ms

    // Reset progress
    setProgress(0)

    // Start progress animation
    let elapsed = 0
    progressRef.current = setInterval(() => {
      elapsed += progressInterval
      setProgress((elapsed / duration) * 100)
    }, progressInterval)

    // Schedule slide change
    slideRef.current = setTimeout(() => {
      setIsTransitioning(true)
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % slides.length)
        setIsTransitioning(false)
      }, 500)
    }, duration)

    return () => {
      if (progressRef.current) clearInterval(progressRef.current)
      if (slideRef.current) clearTimeout(slideRef.current)
    }
  }, [currentIndex, slides.length, defaultDuration])

  if (slides.length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
        <div className="text-center p-8">
          <ImageIcon className="h-16 w-16 text-purple-300 mx-auto mb-4" />
          <p className="text-purple-600 text-lg">No ads to display</p>
          <p className="text-purple-400 text-sm mt-2">
            Upload ads in the admin panel
          </p>
        </div>
      </div>
    )
  }

  const currentSlide = slides[currentIndex]

  return (
    <div className="h-full relative overflow-hidden bg-black flex flex-col">
      {/* Main content area */}
      <div className="flex-1 relative">
        <div
          className={`absolute inset-0 transition-opacity duration-500 ${
            isTransitioning ? "opacity-0" : "opacity-100"
          }`}
        >
          {currentSlide.type === "ad" ? (
            <AdSlide ad={currentSlide.data} />
          ) : (
            <NewsSlide news={currentSlide.data} />
          )}
        </div>
      </div>

      {/* Progress bar at bottom */}
      <div className="h-1.5 bg-gray-800">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-50 ease-linear"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>

      {/* Slide indicators */}
      {slides.length > 1 && (
        <div className="absolute bottom-16 left-0 right-0 flex justify-center gap-2 p-2">
          {slides.map((slide, index) => (
            <div
              key={`${slide.type}-${slide.type === "ad" ? slide.data.id : slide.data.id}`}
              className={`h-2 rounded-full transition-all duration-300 ${
                index === currentIndex
                  ? "w-8 bg-white"
                  : slide.type === "news"
                  ? "w-2 bg-amber-400/50"
                  : "w-2 bg-white/40"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function AdSlide({ ad }: { ad: Ad }) {
  const imageUrl = ad.image_url.startsWith("http")
    ? ad.image_url
    : `${API_URL}${ad.image_url}`

  return (
    <div className="h-full relative">
      <img
        src={imageUrl}
        alt={ad.title}
        className="w-full h-full object-contain bg-gradient-to-br from-gray-900 to-black"
        onError={(e) => {
          const target = e.target as HTMLImageElement
          target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'%3E%3Crect fill='%23374151' width='400' height='300'/%3E%3Ctext fill='%239CA3AF' font-family='sans-serif' font-size='20' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EImage not found%3C/text%3E%3C/svg%3E"
        }}
      />
      
      {/* Ad info overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        <p className="text-white font-medium text-lg">{ad.title}</p>
        {ad.advertiser_name && (
          <p className="text-gray-300 text-sm">{ad.advertiser_name}</p>
        )}
      </div>
    </div>
  )
}

function NewsSlide({ news }: { news: NewsItem }) {
  const imageUrl = news.image_url
    ? news.image_url.startsWith("http")
      ? news.image_url
      : `${API_URL}${news.image_url}`
    : null

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-amber-900 via-amber-800 to-amber-900">
      {/* Header with government branding */}
      <div className="bg-amber-950/50 px-8 py-4 flex items-center gap-4 border-b-2 border-amber-600/50">
        <div className="bg-amber-600 p-3 rounded-xl">
          <Newspaper className="h-8 w-8 text-white" />
        </div>
        <div>
          <p className="text-amber-100 text-xl font-semibold tracking-wide">
            {news.source || "ΚΥΒΕΡΝΗΤΙΚΗ ΑΝΑΚΟΙΝΩΣΗ"}
          </p>
        </div>
      </div>

      {/* Content area - optimized for readability */}
      <div className="flex-1 flex flex-col px-10 py-6 overflow-hidden">
        {/* Greek content (top half) */}
        <div className="flex-1 flex flex-col justify-center border-b-2 border-amber-600/30 pb-6 mb-6">
          <h2 className="text-5xl font-bold text-white mb-4 leading-tight drop-shadow-lg">
            {news.title_el}
          </h2>
          <p className="text-amber-100 text-2xl leading-relaxed line-clamp-3 font-medium">
            {news.content_el}
          </p>
        </div>

        {/* English content (bottom half) */}
        <div className="flex-1 flex flex-col justify-center">
          <h3 className="text-4xl font-bold text-amber-200 mb-3 leading-tight drop-shadow-md">
            {news.title_en || news.title_el}
          </h3>
          <p className="text-amber-100/90 text-xl leading-relaxed line-clamp-3 font-medium">
            {news.content_en || news.content_el}
          </p>
        </div>
      </div>

      {/* Optional image overlay */}
      {imageUrl && (
        <div className="absolute top-24 right-8 w-40 h-40 rounded-xl overflow-hidden shadow-2xl border-4 border-amber-500/50">
          <img
            src={imageUrl}
            alt={news.title_el}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Footer */}
      <div className="bg-amber-950/60 px-8 py-3 border-t-2 border-amber-600/50">
        <p className="text-amber-300 text-lg text-center font-medium tracking-wider">
          🇨🇾 ΚΥΠΡΙΑΚΗ ΔΗΜΟΚΡΑΤΙΑ • REPUBLIC OF CYPRUS
        </p>
      </div>
    </div>
  )
}
