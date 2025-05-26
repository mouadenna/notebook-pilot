import { Plus, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { CellType } from "@/app/types/notebook"

interface NotebookToolbarProps {
  onAddCell: (type: CellType) => void
  onRunAllCells: () => void
}

export function NotebookToolbar({ onAddCell, onRunAllCells }: NotebookToolbarProps) {
  return (
    <div className="border-r bg-white flex-shrink-0">
      <div className="py-2 px-4 flex items-center gap-2">
        <Button size="sm" variant="outline" onClick={() => onAddCell("code")} className="gap-2">
          <Plus className="w-4 h-4" />
          Code Cell
        </Button>
        <Button size="sm" variant="outline" onClick={() => onAddCell("markdown")} className="gap-2">
          <Plus className="w-4 h-4" />
          Markdown Cell
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={onRunAllCells}
          className="gap-2"
        >
          <Play className="w-4 h-4" />
          Run All Cells
        </Button>
      </div>
    </div>
  )
} 