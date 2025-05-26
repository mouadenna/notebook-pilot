"use client"

import { createContext, useContext, useState, ReactNode } from "react"
import { Cell, UploadedFile } from "@/app/types/notebook"

interface NotebookContextType {
  goal: string
  setGoal: (goal: string) => void
  cells: Cell[]
  setCells: (cells: Cell[]) => void
  uploadedFiles: UploadedFile[]
  setUploadedFiles: (files: UploadedFile[]) => void
}

const NotebookContext = createContext<NotebookContextType | undefined>(undefined)

export function NotebookProvider({ children }: { children: ReactNode }) {
  const [goal, setGoal] = useState("")
  const [cells, setCells] = useState<Cell[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])

  return (
    <NotebookContext.Provider
      value={{
        goal,
        setGoal,
        cells,
        setCells,
        uploadedFiles,
        setUploadedFiles,
      }}
    >
      {children}
    </NotebookContext.Provider>
  )
}

export function useNotebook() {
  const context = useContext(NotebookContext)
  if (context === undefined) {
    throw new Error("useNotebook must be used within a NotebookProvider")
  }
  return context
} 