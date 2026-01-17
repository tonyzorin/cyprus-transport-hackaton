"use client"

import { useState, useEffect, useCallback } from "react"
import { useParams } from "next/navigation"
import { ArrivalBoard } from "@/components/ArrivalBoard"
import { AdSlideshow } from "@/components/AdSlideshow"
import { API_URL } from "@/lib/utils"

interface Arrival {
  route_short_name: string
  arrival_time: string
  time_left: number
  trip_headsign: string
  route_color: string
  route_text_color: string
  is_live: boolean
}

interface StopInfo {
  stop_id: string
  stop_name: string
  stop_lat: number | null
  stop_lon: number | null
}

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

interface Alert {
  id: number
  title: string
  message: string
  severity: string
  affected_routes: string | null
  affected_stops: string | null
}

export default function DisplayPage() {
  const params = useParams()
  const stopId = params.stopId as string

  // Arrivals state
  const [stopInfo, setStopInfo] = useState<StopInfo | null>(null)
  const [arrivals, setArrivals] = useState<Arrival[]>([])
  const [arrivalsLoading, setArrivalsLoading] = useState(true)
  const [arrivalsError, setArrivalsError] = useState<string | null>(null)

  // Content state
  const [ads, setAds] = useState<Ad[]>([])
  const [news, setNews] = useState<NewsItem[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])

  // Fetch arrivals
  const fetchArrivals = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/arrivals/${stopId}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setStopInfo(data.stop_info)
      setArrivals(data.arrivals || [])
      setArrivalsError(null)
    } catch (error) {
      console.error("Error fetching arrivals:", error)
      setArrivalsError(error instanceof Error ? error.message : "Failed to fetch arrivals")
    } finally {
      setArrivalsLoading(false)
    }
  }, [stopId])

  // Fetch content (ads, news, alerts)
  const fetchContent = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/content`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setAds(data.ads || [])
      setNews(data.news || [])
      
      // Filter alerts for this stop
      const allAlerts = data.alerts || []
      const relevantAlerts = allAlerts.filter((alert: Alert) => {
        if (!alert.affected_stops) return true // Global alert
        return alert.affected_stops.split(",").includes(stopId)
      })
      setAlerts(relevantAlerts)
    } catch (error) {
      console.error("Error fetching content:", error)
    }
  }, [stopId])

  // Initial fetch
  useEffect(() => {
    fetchArrivals()
    fetchContent()
  }, [fetchArrivals, fetchContent])

  // Auto-refresh arrivals every 30 seconds
  useEffect(() => {
    const arrivalsInterval = setInterval(fetchArrivals, 30000)
    return () => clearInterval(arrivalsInterval)
  }, [fetchArrivals])

  // Auto-refresh content every 5 minutes
  useEffect(() => {
    const contentInterval = setInterval(fetchContent, 300000)
    return () => clearInterval(contentInterval)
  }, [fetchContent])

  return (
    <div className="display-screen h-screen w-screen overflow-hidden bg-black">
      <div className="h-full flex">
        {/* Left side - Bus Arrivals (50%) */}
        <div className="w-1/2 h-full flex flex-col">
          {/* Arrivals board with alerts */}
          <div className="flex-1 overflow-hidden">
            <ArrivalBoard
              stopInfo={stopInfo}
              arrivals={arrivals}
              alerts={alerts}
              loading={arrivalsLoading}
              error={arrivalsError}
            />
          </div>
        </div>

        {/* Right side - Ads & News (50%) */}
        <div className="w-1/2 h-full flex flex-col border-l-4 border-black">
          {/* Ad slideshow with mixed news */}
          <div className="flex-1">
            <AdSlideshow ads={ads} news={news} />
          </div>
        </div>
      </div>
    </div>
  )
}
