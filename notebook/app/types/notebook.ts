import type React from "react"

export type CellType = "code" | "markdown"
export type NotebookPhase = "goal-setting" | "notebook"

export interface Cell {
  id: string
  type: CellType
  content: string
  output?: string
  language?: string
}

export interface UploadedFile {
  id: string
  name: string
  size: string
  type: string
  icon: React.ReactNode
} 