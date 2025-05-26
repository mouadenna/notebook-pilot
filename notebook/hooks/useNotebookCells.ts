import { useState } from "react"
import { Cell, CellType } from "@/app/types/notebook"

export const useNotebookCells = () => {
  const [cells, setCells] = useState<Cell[]>([])
  const [selectedCell, setSelectedCell] = useState<string | null>(null)
  const [runningCellId, setRunningCellId] = useState<string | null>(null)

  const addCell = (type: CellType, afterId?: string) => {
    const newCell: Cell = {
      id: Date.now().toString(),
      type,
      content: "",
      language: type === "code" ? "python" : undefined,
    }

    if (afterId) {
      const index = cells.findIndex((cell) => cell.id === afterId)
      const newCells = [...cells]
      newCells.splice(index + 1, 0, newCell)
      setCells(newCells)
    } else {
      setCells([...cells, newCell])
    }
    setSelectedCell(newCell.id)
  }

  const deleteCell = (id: string) => {
    setCells(cells.filter((cell) => cell.id !== id))
    if (selectedCell === id) {
      setSelectedCell(null)
    }
  }

  const moveCell = (id: string, direction: "up" | "down") => {
    const index = cells.findIndex((cell) => cell.id === id)
    if ((direction === "up" && index === 0) || (direction === "down" && index === cells.length - 1)) {
      return
    }

    const newCells = [...cells]
    const targetIndex = direction === "up" ? index - 1 : index + 1
    ;[newCells[index], newCells[targetIndex]] = [newCells[targetIndex], newCells[index]]
    setCells(newCells)
  }

  const updateCell = (id: string, content: string) => {
    setCells(cells.map((cell) => (cell.id === id ? { ...cell, content } : cell)))
  }

  const runCell = async (id: string) => {
    const cell = cells.find((c) => c.id === id)
    if (!cell || cell.type !== "code") return

    setRunningCellId(id)
    setCells(cells.map((cell) => 
      cell.id === id 
        ? { ...cell, output: undefined }
        : cell
    ))

    try {
      const response = await fetch('/api/python', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: cell.content }),
      })

      const result = await response.json()
      
      setCells(cells.map((cell) => 
        cell.id === id 
          ? { 
              ...cell, 
              output: result.success 
                ? result.output 
                : `Error: ${result.error}`
            } 
          : cell
      ))
    } catch (error) {
      setCells(cells.map((cell) => 
        cell.id === id 
          ? { 
              ...cell, 
              output: `Error: Failed to execute code. ${error instanceof Error ? error.message : 'Unknown error'}`
            } 
          : cell
      ))
    } finally {
      setRunningCellId(null)
    }
  }

  return {
    cells,
    selectedCell,
    setSelectedCell,
    addCell,
    deleteCell,
    moveCell,
    updateCell,
    runCell,
    runningCellId,
  }
} 