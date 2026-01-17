"use client"

import { useState } from "react"
import Link from "next/link"
import { Bus, Image, Newspaper, AlertTriangle, Monitor, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

export default function HomePage() {
  const [stopId, setStopId] = useState("")

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Bus className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Cyprus Transport Hackaton</h1>
              <p className="text-xs text-gray-500">Digital Displays</p>
            </div>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/admin/ads">
              <Button variant="ghost" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Admin
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 pt-8 pb-6">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Digital Displays for Cyprus Bus Stops
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Real-time bus arrivals, ads, government news, and transport alerts
            on a single display system.
          </p>

          {/* Quick Display Access */}
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Monitor className="h-5 w-5" />
                View Display
              </CardTitle>
              <CardDescription>
                Enter a bus stop ID to preview the display screen
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  placeholder="e.g., 6300 or 4338"
                  value={stopId}
                  onChange={(e) => setStopId(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && stopId) {
                      window.location.href = `/display/${stopId}`
                    }
                  }}
                />
                <Link href={stopId ? `/display/${stopId}` : "#"}>
                  <Button disabled={!stopId}>View</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Admin Cards */}
      <section className="container mx-auto px-4 py-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Content Management
        </h3>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {/* Ads Management */}
          <Link href="/admin/ads">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-2">
                  <Image className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle>Ads</CardTitle>
                <CardDescription>
                  Upload and manage ad images for the slideshow
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  Manage Ads
                </Button>
              </CardContent>
            </Card>
          </Link>

          {/* News Management */}
          <Link href="/admin/news">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-2">
                  <Newspaper className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle>Government News</CardTitle>
                <CardDescription>
                  Post government announcements and news
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  Manage News
                </Button>
              </CardContent>
            </Card>
          </Link>

          {/* Alerts Management */}
          <Link href="/admin/alerts">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardHeader>
                <div className="bg-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-2">
                  <AlertTriangle className="h-6 w-6 text-amber-600" />
                </div>
                <CardTitle>Transport Alerts</CardTitle>
                <CardDescription>
                  Create service alerts and disruption notices
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  Manage Alerts
                </Button>
              </CardContent>
            </Card>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white py-8">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          <p>Cyprus Transport Hackaton</p>
          <p className="mt-1">Prototype v1.0</p>
        </div>
      </footer>
    </div>
  )
}
