"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { ArrowLeft, Plus, Trash2, Edit, Upload, Image as ImageIcon, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { API_URL } from "@/lib/utils"

interface Ad {
  id: number
  title: string
  image_url: string
  link_url: string | null
  advertiser_name: string | null
  is_active: boolean
  duration_seconds: number
  created_at: string | null
  expires_at: string | null
}

export default function AdsAdminPage() {
  const [ads, setAds] = useState<Ad[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingAd, setEditingAd] = useState<Ad | null>(null)
  const [formData, setFormData] = useState({
    title: "",
    link_url: "",
    advertiser_name: "",
    duration_seconds: 10,
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch ads
  const fetchAds = async () => {
    try {
      const response = await fetch(`${API_URL}/api/ads?active_only=false`)
      const data = await response.json()
      setAds(data.ads || [])
    } catch (error) {
      console.error("Error fetching ads:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAds()
  }, [])

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
    }
  }

  // Handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const formDataObj = new FormData()
      formDataObj.append("title", formData.title)
      formDataObj.append("duration_seconds", formData.duration_seconds.toString())
      if (formData.link_url) formDataObj.append("link_url", formData.link_url)
      if (formData.advertiser_name) formDataObj.append("advertiser_name", formData.advertiser_name)

      if (editingAd) {
        // Update existing ad
        if (selectedFile) {
          formDataObj.append("image", selectedFile)
        }
        await fetch(`${API_URL}/api/ads/${editingAd.id}`, {
          method: "PUT",
          body: formDataObj,
        })
      } else {
        // Create new ad
        if (!selectedFile) {
          alert("Please select an image")
          setSubmitting(false)
          return
        }
        formDataObj.append("image", selectedFile)
        await fetch(`${API_URL}/api/ads`, {
          method: "POST",
          body: formDataObj,
        })
      }

      // Reset form and refresh
      resetForm()
      fetchAds()
    } catch (error) {
      console.error("Error saving ad:", error)
      alert("Failed to save ad")
    } finally {
      setSubmitting(false)
    }
  }

  // Delete ad
  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this ad?")) return

    try {
      await fetch(`${API_URL}/api/ads/${id}`, { method: "DELETE" })
      fetchAds()
    } catch (error) {
      console.error("Error deleting ad:", error)
    }
  }

  // Toggle active status
  const toggleActive = async (ad: Ad) => {
    try {
      const formDataObj = new FormData()
      formDataObj.append("is_active", (!ad.is_active).toString())
      await fetch(`${API_URL}/api/ads/${ad.id}`, {
        method: "PUT",
        body: formDataObj,
      })
      fetchAds()
    } catch (error) {
      console.error("Error toggling ad status:", error)
    }
  }

  // Edit ad
  const handleEdit = (ad: Ad) => {
    setEditingAd(ad)
    setFormData({
      title: ad.title,
      link_url: ad.link_url || "",
      advertiser_name: ad.advertiser_name || "",
      duration_seconds: ad.duration_seconds,
    })
    setPreviewUrl(`${API_URL}${ad.image_url}`)
    setShowForm(true)
  }

  // Reset form
  const resetForm = () => {
    setShowForm(false)
    setEditingAd(null)
    setFormData({ title: "", link_url: "", advertiser_name: "", duration_seconds: 10 })
    setSelectedFile(null)
    setPreviewUrl(null)
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
            <h1 className="text-xl font-bold">Manage Advertisements</h1>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Ad
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>{editingAd ? "Edit Ad" : "Add New Ad"}</CardTitle>
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
                    <Label htmlFor="image">Image {!editingAd && "*"}</Label>
                    <div
                      className="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:bg-gray-50 hover:border-blue-400 transition-colors"
                      onClick={() => fileInputRef.current?.click()}
                      onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
                      tabIndex={0}
                      role="button"
                      aria-label="Click to upload image"
                    >
                      {previewUrl ? (
                        <img src={previewUrl} alt="Preview" className="max-h-40 mx-auto rounded pointer-events-none" />
                      ) : (
                        <div className="py-8 pointer-events-none">
                          <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                          <p className="text-sm text-gray-500">Click to upload image</p>
                          <p className="text-xs text-gray-400 mt-1">JPG, PNG, GIF up to 10MB</p>
                        </div>
                      )}
                    </div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </div>

                  <div>
                    <Label htmlFor="advertiser_name">Advertiser Name</Label>
                    <Input
                      id="advertiser_name"
                      value={formData.advertiser_name}
                      onChange={(e) => setFormData({ ...formData, advertiser_name: e.target.value })}
                    />
                  </div>

                  <div>
                    <Label htmlFor="link_url">Link URL</Label>
                    <Input
                      id="link_url"
                      type="url"
                      value={formData.link_url}
                      onChange={(e) => setFormData({ ...formData, link_url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>

                  <div>
                    <Label htmlFor="duration">Display Duration (seconds)</Label>
                    <Input
                      id="duration"
                      type="number"
                      min="5"
                      max="60"
                      value={formData.duration_seconds}
                      onChange={(e) => setFormData({ ...formData, duration_seconds: parseInt(e.target.value) })}
                    />
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button type="button" variant="outline" onClick={resetForm} className="flex-1">
                      Cancel
                    </Button>
                    <Button type="submit" disabled={submitting} className="flex-1">
                      {submitting ? "Saving..." : editingAd ? "Update" : "Create"}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Ads Grid */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : ads.length === 0 ? (
          <div className="text-center py-12">
            <ImageIcon className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No ads yet. Click "Add Ad" to create one.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ads.map((ad) => (
              <Card key={ad.id} className={!ad.is_active ? "opacity-60" : ""}>
                <div className="aspect-video bg-gray-100 relative">
                  <img
                    src={`${API_URL}${ad.image_url}`}
                    alt={ad.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='225' viewBox='0 0 400 225'%3E%3Crect fill='%23f3f4f6' width='400' height='225'/%3E%3Ctext fill='%239ca3af' font-family='sans-serif' font-size='14' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EImage not found%3C/text%3E%3C/svg%3E"
                    }}
                  />
                  <Badge
                    className="absolute top-2 right-2"
                    variant={ad.is_active ? "success" : "secondary"}
                  >
                    {ad.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                <CardContent className="p-4">
                  <h3 className="font-medium mb-1">{ad.title}</h3>
                  {ad.advertiser_name && (
                    <p className="text-sm text-gray-500 mb-2">{ad.advertiser_name}</p>
                  )}
                  <p className="text-xs text-gray-400 mb-3">
                    Duration: {ad.duration_seconds}s
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => toggleActive(ad)}
                    >
                      {ad.is_active ? "Deactivate" : "Activate"}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(ad)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(ad.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
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
