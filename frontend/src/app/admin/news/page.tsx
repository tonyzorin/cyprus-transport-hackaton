"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { ArrowLeft, Plus, Trash2, Edit, Newspaper, X, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { API_URL } from "@/lib/utils"

interface NewsItem {
  id: number
  title: string
  content: string
  image_url: string | null
  source: string | null
  is_active: boolean
  created_at: string | null
  expires_at: string | null
}

export default function NewsAdminPage() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingNews, setEditingNews] = useState<NewsItem | null>(null)
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    source: "",
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Fetch news
  const fetchNews = async () => {
    try {
      const response = await fetch(`${API_URL}/api/news?active_only=false`)
      const data = await response.json()
      setNews(data.news || [])
    } catch (error) {
      console.error("Error fetching news:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNews()
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
      formDataObj.append("content", formData.content)
      if (formData.source) formDataObj.append("source", formData.source)
      if (selectedFile) formDataObj.append("image", selectedFile)

      if (editingNews) {
        await fetch(`${API_URL}/api/news/${editingNews.id}`, {
          method: "PUT",
          body: formDataObj,
        })
      } else {
        await fetch(`${API_URL}/api/news`, {
          method: "POST",
          body: formDataObj,
        })
      }

      resetForm()
      fetchNews()
    } catch (error) {
      console.error("Error saving news:", error)
      alert("Failed to save news")
    } finally {
      setSubmitting(false)
    }
  }

  // Delete news
  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this news item?")) return

    try {
      await fetch(`${API_URL}/api/news/${id}`, { method: "DELETE" })
      fetchNews()
    } catch (error) {
      console.error("Error deleting news:", error)
    }
  }

  // Toggle active status
  const toggleActive = async (item: NewsItem) => {
    try {
      const formDataObj = new FormData()
      formDataObj.append("is_active", (!item.is_active).toString())
      await fetch(`${API_URL}/api/news/${item.id}`, {
        method: "PUT",
        body: formDataObj,
      })
      fetchNews()
    } catch (error) {
      console.error("Error toggling news status:", error)
    }
  }

  // Edit news
  const handleEdit = (item: NewsItem) => {
    setEditingNews(item)
    setFormData({
      title: item.title,
      content: item.content,
      source: item.source || "",
    })
    if (item.image_url) {
      setPreviewUrl(`${API_URL}${item.image_url}`)
    }
    setShowForm(true)
  }

  // Reset form
  const resetForm = () => {
    setShowForm(false)
    setEditingNews(null)
    setFormData({ title: "", content: "", source: "" })
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
            <h1 className="text-xl font-bold">Manage Government News</h1>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add News
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>{editingNews ? "Edit News" : "Add News Item"}</CardTitle>
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
                    <Label htmlFor="content">Content *</Label>
                    <Textarea
                      id="content"
                      value={formData.content}
                      onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                      rows={4}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="source">Source</Label>
                    <Input
                      id="source"
                      value={formData.source}
                      onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                      placeholder="e.g., Ministry of Transport"
                    />
                  </div>

                  <div>
                    <Label htmlFor="image">Image (optional)</Label>
                    <div
                      className="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:bg-gray-50"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      {previewUrl ? (
                        <img src={previewUrl} alt="Preview" className="max-h-40 mx-auto rounded" />
                      ) : (
                        <div className="py-4">
                          <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                          <p className="text-sm text-gray-500">Click to upload image</p>
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

                  <div className="flex gap-2 pt-4">
                    <Button type="button" variant="outline" onClick={resetForm} className="flex-1">
                      Cancel
                    </Button>
                    <Button type="submit" disabled={submitting} className="flex-1">
                      {submitting ? "Saving..." : editingNews ? "Update" : "Create"}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}

        {/* News List */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : news.length === 0 ? (
          <div className="text-center py-12">
            <Newspaper className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No news yet. Click "Add News" to create one.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {news.map((item) => (
              <Card key={item.id} className={!item.is_active ? "opacity-60" : ""}>
                <CardContent className="p-4">
                  <div className="flex gap-4">
                    {item.image_url && (
                      <img
                        src={`${API_URL}${item.image_url}`}
                        alt={item.title}
                        className="w-24 h-24 object-cover rounded"
                      />
                    )}
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium">{item.title}</h3>
                          {item.source && (
                            <p className="text-sm text-gray-500">{item.source}</p>
                          )}
                        </div>
                        <Badge variant={item.is_active ? "success" : "secondary"}>
                          {item.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">{item.content}</p>
                      <div className="flex gap-2 mt-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleActive(item)}
                        >
                          {item.is_active ? "Deactivate" : "Activate"}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(item)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(item.id)}
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
