import { UploadedFile } from "@/app/types/notebook"
import { Button } from "@/components/ui/button"
import { Upload, X } from "lucide-react"

interface FileUploadProps {
  uploadedFiles: UploadedFile[]
  isDragOver: boolean
  onDrop: (e: React.DragEvent) => void
  onDragOver: (e: React.DragEvent) => void
  onDragLeave: (e: React.DragEvent) => void
  onFileUpload: (files: FileList) => void
  onRemoveFile: (id: string) => void
}

export function FileUpload({
  uploadedFiles,
  isDragOver,
  onDrop,
  onDragOver,
  onDragLeave,
  onFileUpload,
  onRemoveFile,
}: FileUploadProps) {
  return (
    <div className="flex-1 flex flex-col">
      {/* Drop Zone */}
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={`flex-1 border-2 border-dashed rounded-lg transition-all duration-200 ${
          isDragOver ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
        } flex flex-col items-center justify-center p-8 cursor-pointer`}
        onClick={() => document.getElementById("file-upload")?.click()}
      >
        <Upload className={`w-12 h-12 mb-4 ${isDragOver ? "text-blue-500" : "text-gray-400"}`} />
        <h3 className={`text-lg font-medium mb-2 ${isDragOver ? "text-blue-700" : "text-gray-700"}`}>
          {isDragOver ? "Drop files here" : "Drag & drop files here"}
        </h3>
        <p className="text-gray-500 mb-4">or click to browse</p>
        <div className="text-sm text-gray-400">
          Supports: CSV, Excel, Images, Python files, Jupyter notebooks
        </div>

        <input
          id="file-upload"
          type="file"
          multiple
          onChange={(e) => e.target.files && onFileUpload(e.target.files)}
          className="hidden"
          accept=".csv,.xlsx,.xls,.json,.txt,.py,.ipynb,.jpg,.jpeg,.png,.gif"
        />
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6 max-h-48 overflow-y-auto">
          <h4 className="font-medium text-gray-700 mb-3">Uploaded Files ({uploadedFiles.length})</h4>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                {file.icon}
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 truncate">{file.name}</div>
                  <div className="text-sm text-gray-500">{file.size}</div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onRemoveFile(file.id)}
                  className="text-gray-400 hover:text-red-500 p-1"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 