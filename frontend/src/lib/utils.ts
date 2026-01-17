import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// API base URL
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Fetch wrapper with error handling
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Format time left for display
export function formatTimeLeft(minutes: number): string {
  if (minutes < 1) {
    return "Now"
  } else if (minutes === 1) {
    return "1 min"
  } else if (minutes < 60) {
    return `${minutes} min`
  } else {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }
}

// Get color class based on time left
export function getTimeColor(minutes: number): string {
  if (minutes <= 5) {
    return "text-green-600 font-bold"
  } else if (minutes <= 15) {
    return "text-blue-600"
  } else {
    return "text-gray-600"
  }
}

// Get alert severity color
export function getAlertColor(severity: string): string {
  switch (severity) {
    case "critical":
      return "bg-red-500"
    case "warning":
      return "bg-amber-500"
    default:
      return "bg-blue-500"
  }
}
