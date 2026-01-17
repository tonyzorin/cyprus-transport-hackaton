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
  | { type: "placeholder" }

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
  // Add placeholder slide when there are no ads
  const slides: SlideItem[] = [
    ...ads.map((ad): SlideItem => ({ type: "ad", data: ad })),
    ...news.map((item): SlideItem => ({ type: "news", data: item })),
    // Add "Advertise Here" placeholder when no ads exist
    ...(ads.length === 0 ? [{ type: "placeholder" } as SlideItem] : []),
  ]

  // Get duration for current slide
  const getCurrentDuration = () => {
    if (slides.length === 0) return defaultDuration
    const currentSlide = slides[currentIndex]
    if (currentSlide.type === "ad") {
      return currentSlide.data.duration_seconds || defaultDuration
    } else if (currentSlide.type === "news") {
      return currentSlide.data.duration_seconds || 12
    } else {
      // Placeholder duration
      return defaultDuration
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
          ) : currentSlide.type === "news" ? (
            <NewsSlide news={currentSlide.data} />
          ) : (
            <PlaceholderSlide />
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
              key={`${slide.type}-${slide.type === "ad" ? slide.data.id : slide.type === "news" ? slide.data.id : "placeholder"}`}
              className={`h-2 rounded-full transition-all duration-300 ${
                index === currentIndex
                  ? "w-8 bg-white"
                  : slide.type === "news"
                  ? "w-2 bg-amber-400/50"
                  : slide.type === "placeholder"
                  ? "w-2 bg-indigo-400/50"
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

function PlaceholderSlide() {
  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 relative overflow-hidden">
      {/* Animated background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(99, 102, 241, 0.3) 0%, transparent 50%),
                            radial-gradient(circle at 75% 75%, rgba(168, 85, 247, 0.3) 0%, transparent 50%)`
        }} />
      </div>
      
      {/* Main content */}
      <div className="relative z-10 flex flex-col items-center gap-8 p-8 max-w-2xl">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-1.5 rounded-full text-sm font-bold tracking-wider uppercase shadow-lg">
            <span className="animate-pulse">●</span>
            Διαφημιστικός Χώρος • Ad Space
          </div>
        </div>

        {/* QR Code Card */}
        <div className="bg-white/95 backdrop-blur-sm rounded-3xl p-8 shadow-2xl border border-white/20">
          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* QR Code */}
            <div className="bg-white p-4 rounded-2xl shadow-inner border-4 border-indigo-100">
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent('https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1')}&bgcolor=ffffff&color=1e1b4b`}
                alt="Scan to advertise"
                className="w-44 h-44"
              />
            </div>
            
            {/* Text content */}
            <div className="text-center md:text-left space-y-4">
              <div className="space-y-1">
                <h2 className="text-2xl font-bold text-slate-800 leading-tight">
                  Διαφημιστείτε Εδώ!
                </h2>
                <h3 className="text-xl font-semibold text-indigo-600">
                  Advertise Here!
                </h3>
              </div>
              
              <p className="text-slate-600 text-sm leading-relaxed max-w-xs">
                Σαρώστε τον κωδικό QR για να μάθετε περισσότερα
                <br />
                <span className="text-slate-500">Scan the QR code to learn more</span>
              </p>
            </div>
          </div>
        </div>

        {/* Footer tagline */}
        <div className="text-center space-y-1">
          <p className="text-indigo-300 text-sm font-medium">
            Προσεγγίστε χιλιάδες επιβάτες καθημερινά
          </p>
          <p className="text-indigo-400/70 text-xs">
            Reach thousands of passengers daily
          </p>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-10 left-10 w-20 h-20 border-2 border-indigo-500/20 rounded-full animate-pulse" />
      <div className="absolute bottom-10 right-10 w-32 h-32 border-2 border-purple-500/20 rounded-full animate-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/2 right-20 w-16 h-16 border-2 border-amber-500/20 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }} />
    </div>
  )
}
