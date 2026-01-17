"use client"

import { AlertTriangle, Info, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface Alert {
  id: number
  title: string
  message: string
  severity: string
  affected_routes: string | null
}

interface TransportAlertProps {
  alerts: Alert[]
}

export function TransportAlert({ alerts }: TransportAlertProps) {
  if (alerts.length === 0) return null

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
        "p-3 flex items-center gap-3 text-white",
        alert.severity === "critical" && "bg-red-600 animate-pulse",
        alert.severity === "warning" && "bg-amber-500",
        alert.severity === "info" && "bg-blue-500"
      )}
    >
      <Icon className="h-5 w-5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate">{alert.title}</p>
        <p className="text-sm opacity-90 truncate">{alert.message}</p>
      </div>
      {alerts.length > 1 && (
        <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
          +{alerts.length - 1} more
        </span>
      )}
    </div>
  )
}
