import { useState } from "react"
import { UploadedFile } from "@/app/types/notebook"
import { Code, File, ImageIcon, Database, LucideIcon } from "lucide-react"

export const useFileUpload = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isDragOver, setIsDragOver] = useState(false)

  const getFileIcon = (fileName: string): LucideIcon => {
    const extension = fileName.split(".").pop()?.toLowerCase()
    switch (extension) {
      case "csv":
      case "xlsx":
      case "xls":
        return Database
      case "jpg":
      case "jpeg":
      case "png":
      case "gif":
        return ImageIcon
      case "py":
      case "ipynb":
        return Code
      default:
        return File
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const handleFileUpload = (files: FileList) => {
    const newFiles: UploadedFile[] = Array.from(files).map((file) => {
      const IconComponent = getFileIcon(file.name)
      return {
        id: Date.now().toString() + Math.random(),
        name: file.name,
        size: formatFileSize(file.size),
        type: file.type,
        icon: IconComponent({ className: "w-5 h-5 text-gray-600" }),
      }
    })
    setUploadedFiles([...uploadedFiles, ...newFiles])
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const removeFile = (id: string) => {
    setUploadedFiles(uploadedFiles.filter((file) => file.id !== id))
  }

  return {
    uploadedFiles,
    isDragOver,
    handleFileUpload,
    handleDrop,
    handleDragOver,
    handleDragLeave,
    removeFile,
  }
} 