"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { ArrowLeft, Plus, Trash2, Edit, AlertTriangle, X, AlertCircle, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { API_URL, cn } from "@/lib/utils"

interface Alert {
  id: number
  title: string
  message: string
  severity: string
  affected_routes: string | null
  affected_stops: string | null
  is_active: boolean
  created_at: string | null
  expires_at: string | null
}

export default function AlertsAdminPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null)
  const [formData, setFormData] = useState({
    title: "",
    message: "",
    severity: "info",
    affected_routes: "",
    affected_stops: "",
  })
  const [submitting, setSubmitting] = useState(false)

  // Fetch alerts
  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/alerts?active_only=false`)
      const data = await response.json()
      setAlerts(data.alerts || [])
    } catch (error) {
      console.error("Error fetching alerts:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [])

  // Handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const payload = {
        title: formData.title,
        message: formData.message,
        severity: formData.severity,
        affected_routes: formData.affected_routes || null,
        affected_stops: formData.affected_stops || null,
      }

      if (editingAlert) {
        await fetch(`${API_URL}/api/alerts/${editingAlert.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })
      } else {
        await fetch(`${API_URL}/api/alerts`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })
      }

      resetForm()
      fetchAlerts()
    } catch (error) {
      console.error("Error saving alert:", error)
      alert("Failed to save alert")
    } finally {
      setSubmitting(false)
    }
  }

  // Delete alert
  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this alert?")) return

    try {
      await fetch(`${API_URL}/api/alerts/${id}`, { method: "DELETE" })
      fetchAlerts()
    } catch (error) {
      console.error("Error deleting alert:", error)
    }
  }

  // Toggle active status
  const toggleActive = async (alert: Alert) => {
    try {
      await fetch(`${API_URL}/api/alerts/${alert.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !alert.is_active }),
      })
      fetchAlerts()
    } catch (error) {
      console.error("Error toggling alert status:", error)
    }
  }

  // Edit alert
  const handleEdit = (alert: Alert) => {
    setEditingAlert(alert)
    setFormData({
      title: alert.title,
      message: alert.message,
      severity: alert.severity,
      affected_routes: alert.affected_routes || "",
      affected_stops: alert.affected_stops || "",
    })
    setShowForm(true)
  }

  // Reset form
  const resetForm = () => {
    setShowForm(false)
    setEditingAlert(null)
    setFormData({
      title: "",
      message: "",
      severity: "info",
      affected_routes: "",
      affected_stops: "",
    })
  }

  // Get severity icon
  const SeverityIcon = ({ severity }: { severity: string }) => {
    switch (severity) {
      case "critical":
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-amber-500" />
      default:
        return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <h1 className="text-xl font-bold">Manage Transport Alerts</h1>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Alert
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>{editingAlert ? "Edit Alert" : "Create Alert"}</CardTitle>
                <Button variant="ghost" size="icon" onClick={resetForm}>
                  <X className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="title">Title *</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="message">Message *</Label>
                    <Textarea
                      id="message"
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      rows={3}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="severity">Severity *</Label>
                    <div className="flex gap-2 mt-2">
                      {["info", "warning", "critical"].map((sev) => (
                        <Button
                          key={sev}
                          type="button"
                          variant={formData.severity === sev ? "default" : "outline"}
                          size="sm"
                          onClick={() => setFormData({ ...formData, severity: sev })}
                          className={cn(
                            formData.severity === sev && sev === "info" && "bg-blue-500 hover:bg-blue-600",
                            formData.severity === sev && sev === "warning" && "bg-amber-500 hover:bg-amber-600",
                            formData.severity === sev && sev === "critical" && "bg-red-500 hover:bg-red-600"
                          )}
                        >
                          {sev.charAt(0).toUpperCase() + sev.slice(1)}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="affected_routes">Affected Routes</Label>
                    <Input
                      id="affected_routes"
                      value={formData.affected_routes}
                      onChange={(e) => setFormData({ ...formData, affected_routes: e.target.value })}
                      placeholder="e.g., 30, 15, 7 (comma-separated)"
                    />
                    <p className="text-xs text-gray-500 mt-1">Leave empty for all routes</p>
                  </div>

                  <div>
                    <Label htmlFor="affected_stops">Affected Stops</Label>
                    <Input
                      id="affected_stops"
                      value={formData.affected_stops}
                      onChange={(e) => setFormData({ ...formData, affected_stops: e.target.value })}
                      placeholder="e.g., LIM-001, LIM-002 (comma-separated)"
                    />
                    <p className="text-xs text-gray-500 mt-1">Leave empty for all stops</p>
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button type="button" variant="outline" onClick={resetForm} className="flex-1">
                      Cancel
                    </Button>
                    <Button type="submit" disabled={submitting} className="flex-1">
                      {submitting ? "Saving..." : editingAlert ? "Update" : "Create"}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Alerts List */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-12">
            <AlertTriangle className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No alerts yet. Click "Add Alert" to create one.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <Card key={alert.id} className={!alert.is_active ? "opacity-60" : ""}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <SeverityIcon severity={alert.severity} />
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium">{alert.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge
                            variant={
                              alert.severity === "critical"
                                ? "destructive"
                                : alert.severity === "warning"
                                ? "warning"
                                : "default"
                            }
                          >
                            {alert.severity}
                          </Badge>
                          <Badge variant={alert.is_active ? "success" : "secondary"}>
                            {alert.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </div>
                      </div>
                      {(alert.affected_routes || alert.affected_stops) && (
                        <div className="flex gap-4 mt-2 text-xs text-gray-500">
                          {alert.affected_routes && (
                            <span>Routes: {alert.affected_routes}</span>
                          )}
                          {alert.affected_stops && (
                            <span>Stops: {alert.affected_stops}</span>
                          )}
                        </div>
                      )}
                      <div className="flex gap-2 mt-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleActive(alert)}
                        >
                          {alert.is_active ? "Deactivate" : "Activate"}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(alert)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(alert.id)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
