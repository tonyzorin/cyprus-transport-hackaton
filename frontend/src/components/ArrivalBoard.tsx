"use client"

import { useState, useEffect } from "react"
import { Bus, Clock, MapPin, AlertTriangle, Info, AlertCircle, Calendar } from "lucide-react"
import { formatTimeLeft, getTimeColor, cn } from "@/lib/utils"

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

interface Alert {
  id: number
  title: string
  message: string
  severity: string
  affected_routes: string | null
}

interface ArrivalBoardProps {
  stopInfo: StopInfo | null
  arrivals: Arrival[]
  alerts?: Alert[]
  loading?: boolean
  error?: string | null
}

export function ArrivalBoard({ stopInfo, arrivals, alerts = [], loading, error }: ArrivalBoardProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // Format date and time for display
  const formattedDate = currentTime.toLocaleDateString("en-CY", {
    weekday: "short",
    day: "numeric",
    month: "short",
  })
  
  const formattedTime = currentTime.toLocaleTimeString("en-CY", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-blue-900 to-blue-950">
        <div className="text-center">
          <Bus className="h-16 w-16 text-blue-300 animate-pulse mx-auto mb-4" />
          <p className="text-blue-200 text-xl">Loading arrivals...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-red-900 to-red-950">
        <div className="text-center p-8">
          <p className="text-red-200 text-xl mb-2">Error loading arrivals</p>
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-blue-900 to-blue-950 text-white">
      {/* Header with stop info and date/time */}
      <div className="bg-blue-800/50 p-4 border-b border-blue-700">
        <div className="flex items-center justify-between">
          {/* Stop info - left side */}
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <MapPin className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold truncate">
                {stopInfo?.stop_name || "Bus Stop"}
              </h2>
              <p className="text-blue-300 text-sm">
                Stop ID: {stopInfo?.stop_id || "Unknown"}
              </p>
            </div>
          </div>
          
          {/* Date/Time - right side */}
          <div className="text-right">
            <p className="text-3xl font-bold text-white tabular-nums">
              {formattedTime}
            </p>
            <p className="text-blue-300 text-sm">
              {formattedDate}
            </p>
          </div>
        </div>
      </div>

      {/* Arrivals list */}
      <div className="flex-1 overflow-hidden">
        {arrivals.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center p-8">
              <Clock className="h-12 w-12 text-blue-400 mx-auto mb-4" />
              <p className="text-blue-200 text-lg">No upcoming arrivals</p>
              <p className="text-blue-400 text-sm mt-2">
                Check back later for bus times
              </p>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-blue-800/50">
            {arrivals.slice(0, 8).map((arrival, index) => (
              <ArrivalRow key={index} arrival={arrival} index={index} />
            ))}
          </div>
        )}
      </div>

      {/* Alerts section - above footer */}
      {alerts.length > 0 && <AlertBanner alerts={alerts} />}

      {/* Footer */}
      <div className="bg-blue-800/30 p-3 border-t border-blue-700">
        <div className="flex items-center justify-between text-sm text-blue-300">
          <span className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            Real-time data
          </span>
          <span className="text-blue-400/70 text-xs">
            Prototype v1.0
          </span>
          <span>
            Updated: {currentTime.toLocaleTimeString("en-CY", { 
              hour: "2-digit", 
              minute: "2-digit",
              hour12: false
            })}
          </span>
        </div>
      </div>
    </div>
  )
}

function ArrivalRow({ arrival, index }: { arrival: Arrival; index: number }) {
  const routeColor = arrival.route_color ? `#${arrival.route_color}` : "#3b82f6"
  const textColor = arrival.route_text_color ? `#${arrival.route_text_color}` : "#ffffff"

  return (
    <div 
      className="p-4 flex items-center gap-5 hover:bg-blue-800/30 transition-colors animate-fade-in"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Route badge */}
      <div
        className="min-w-[90px] h-16 rounded-xl flex items-center justify-center font-bold text-3xl shadow-lg"
        style={{ backgroundColor: routeColor, color: textColor }}
      >
        {arrival.route_short_name}
      </div>

      {/* Destination */}
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-white text-xl truncate">
          {arrival.trip_headsign || "Unknown Destination"}
        </p>
        <p className="text-blue-300 text-base">
          {formatArrivalTime(arrival.arrival_time)}
        </p>
      </div>

      {/* Time left */}
      <div className="text-right">
        <p className={`text-3xl font-bold ${getArrivalTimeColor(arrival.time_left)}`}>
          {formatTimeLeft(arrival.time_left)}
        </p>
        {arrival.is_live && (
          <span className="text-sm text-green-400 flex items-center justify-end gap-1">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Live
          </span>
        )}
      </div>
    </div>
  )
}

function getArrivalTimeColor(minutes: number): string {
  if (minutes <= 5) {
    return "text-green-400"
  } else if (minutes <= 15) {
    return "text-yellow-400"
  } else {
    return "text-blue-200"
  }
}

function formatArrivalTime(time: string): string {
  // Remove seconds from time string (e.g., "13:16:06" -> "13:16")
  const parts = time.split(":")
  if (parts.length >= 2) {
    return `${parts[0]}:${parts[1]}`
  }
  return time
}

function AlertBanner({ alerts }: { alerts: Alert[] }) {
  // Show the most severe alert
  const sortedAlerts = [...alerts].sort((a, b) => {
    const severityOrder = { critical: 0, warning: 1, info: 2 }
    return (severityOrder[a.severity as keyof typeof severityOrder] || 2) -
           (severityOrder[b.severity as keyof typeof severityOrder] || 2)
  })

  const alert = sortedAlerts[0]

  const Icon = alert.severity === "critical" 
    ? AlertCircle 
    : alert.severity === "warning" 
    ? AlertTriangle 
    : Info

  return (
    <div
      className={cn(
        "p-4 flex items-start gap-3 text-white",
        alert.severity === "critical" && "bg-red-600 animate-pulse",
        alert.severity === "warning" && "bg-amber-500",
        alert.severity === "info" && "bg-blue-500"
      )}
    >
      <Icon className="h-6 w-6 flex-shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-base leading-tight">{alert.title}</p>
        <p className="text-sm opacity-90 leading-snug">{alert.message}</p>
      </div>
      {alerts.length > 1 && (
        <span className="text-xs bg-white/20 px-2 py-1 rounded-full flex-shrink-0">
          +{alerts.length - 1} more
        </span>
      )}
    </div>
  )
}
