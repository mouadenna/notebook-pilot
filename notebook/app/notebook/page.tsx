"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FileText, Settings, Moon, Sun, Play, Plus, Target } from "lucide-react"
import { useTheme } from "next-themes"
import { NotebookCell } from "@/components/notebook/NotebookCell"
import { useNotebookCells } from "@/hooks/useNotebookCells"
import { NotebookToolbar } from "@/components/notebook/NotebookToolbar"

export default function NotebookPage() {
  const { theme, setTheme } = useTheme()
  const {
    cells,
    selectedCell,
    setSelectedCell,
    addCell,
    deleteCell,
    moveCell,
    updateCell,
    runCell,
    runningCellId,
  } = useNotebookCells()

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="border-b bg-white flex-shrink-0">
        <div className="px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-600" />
                <h1 className="text-xl font-semibold">Notebook Pilot</h1>
              </div>
              <Badge variant="secondary">Generated</Badge>
            </div>

            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
                {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Project Info */}
        <div className="w-80 border-r bg-gray-50 flex-shrink-0 overflow-y-auto">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              Project Goal
            </h3>

            <div className="bg-white p-4 rounded-lg border mb-6">
              <p className="text-sm leading-relaxed text-gray-700">
                {/* TODO: Get goal from context/state management */}
                Your project goal will appear here
              </p>
            </div>
          </div>
        </div>

        {/* Center - Notebook Content with Toolbar */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Toolbar */}
          <NotebookToolbar
            onAddCell={addCell}
            onRunAllCells={() => {
              cells.forEach((cell) => {
                if (cell.type === "code") {
                  runCell(cell.id)
                }
              })
            }}
          />

          {/* Notebook Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6">
              <div className="max-w-4xl mx-auto space-y-4">
                {cells.map((cell) => (
                  <NotebookCell
                    key={cell.id}
                    cell={cell}
                    isSelected={selectedCell === cell.id}
                    isRunning={runningCellId === cell.id}
                    onSelect={() => setSelectedCell(cell.id)}
                    onUpdate={(content) => updateCell(cell.id, content)}
                    onDelete={() => deleteCell(cell.id)}
                    onMove={(direction) => moveCell(cell.id, direction)}
                    onRun={() => runCell(cell.id)}
                    onAddCell={(type) => addCell(type, cell.id)}
                    onLanguageChange={(language) => {
                      const updatedCells = cells.map((c) =>
                        c.id === cell.id ? { ...c, language } : c
                      )
                      // TODO: Update cells state
                    }}
                  />
                ))}

                {/* Add cell at the end */}
                <div className="flex gap-2 justify-center py-4">
                  <Button variant="outline" onClick={() => addCell("code")} className="gap-2">
                    <Plus className="w-4 h-4" />
                    Code Cell
                  </Button>
                  <Button variant="outline" onClick={() => addCell("markdown")} className="gap-2">
                    <Plus className="w-4 h-4" />
                    Markdown Cell
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 