import { Cell } from "@/app/types/notebook"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Play, ChevronUp, ChevronDown, Trash2, Code, Type, Plus, Loader2 } from "lucide-react"
import { Highlight, themes } from "prism-react-renderer"

interface NotebookCellProps {
  cell: Cell
  isSelected: boolean
  isRunning?: boolean
  onSelect: () => void
  onUpdate: (content: string) => void
  onDelete: () => void
  onMove: (direction: "up" | "down") => void
  onRun: () => void
  onAddCell: (type: "code" | "markdown") => void
  onLanguageChange: (language: string) => void
}

export function NotebookCell({
  cell,
  isSelected,
  isRunning = false,
  onSelect,
  onUpdate,
  onDelete,
  onMove,
  onRun,
  onAddCell,
  onLanguageChange,
}: NotebookCellProps) {
  const renderMarkdown = (content: string) => {
    return content
      // Headers
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-4 mb-2">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold mt-3 mb-2">$1</h3>')
      // Bold and Italic
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // Code blocks
      .replace(/```(\w+)?\n([\s\S]*?)```/g, (_, language, code) => {
        return `<div class="bg-slate-100 dark:bg-slate-800 p-3 rounded-md my-2">
          <pre class="text-sm font-mono">${code.trim()}</pre>
        </div>`
      })
      // Inline code
      .replace(/`([^`]+)`/g, '<code class="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 hover:underline" target="_blank">$1</a>')
      // Blockquotes
      .replace(/^> (.*$)/gm, '<blockquote class="border-l-4 border-gray-300 pl-4 my-2 italic">$1</blockquote>')
      // Lists
      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4">$1</li>')
      .replace(/^- (.*$)/gm, '<li class="ml-4">$1</li>')
      // Horizontal rule
      .replace(/^---$/gm, '<hr class="my-4 border-t border-gray-300">')
      // Line breaks
      .replace(/\n/g, '<br>')
  }

  return (
    <Card
      className={`mb-4 transition-all duration-200 ${
        isSelected ? "ring-2 ring-blue-500 shadow-lg" : "hover:shadow-md"
      }`}
      onClick={onSelect}
    >
      <div className="flex items-center justify-between p-2 border-b bg-muted/30">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            {cell.type === "code" ? (
              <>
                <Code className="w-3 h-3 mr-1" />
                Python
              </>
            ) : (
              <>
                <Type className="w-3 h-3 mr-1" />
                markdown
              </>
            )}
          </Badge>
        </div>
        <div className="flex items-center gap-1">
          {cell.type === "code" && (
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={(e) => { e.stopPropagation(); onRun() }} 
              className="h-7 px-2"
              disabled={isRunning}
            >
              {isRunning ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Play className="w-3 h-3" />
              )}
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); onMove("up") }} className="h-7 px-2">
            <ChevronUp className="w-3 h-3" />
          </Button>
          <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); onMove("down") }} className="h-7 px-2">
            <ChevronDown className="w-3 h-3" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => { e.stopPropagation(); onDelete() }}
            className="h-7 px-2 text-red-500 hover:text-red-700"
          >
            <Trash2 className="w-3 h-3" />
          </Button>
        </div>
      </div>

      <div className="p-4">
        {cell.type === "markdown" ? (
          <div className="space-y-4">
            <Textarea
              value={cell.content}
              onChange={(e) => onUpdate(e.target.value)}
              className="min-h-[100px] font-mono text-sm"
              placeholder="Enter markdown content..."
            />
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <div
                dangerouslySetInnerHTML={{
                  __html: renderMarkdown(cell.content)
                }}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <div className="relative">
                <Textarea
                  value={cell.content}
                  onChange={(e) => onUpdate(e.target.value)}
                  className="min-h-[120px] font-mono text-sm bg-transparent absolute inset-0 z-10 resize-none caret-black dark:caret-white font-medium"
                  placeholder="Enter your Python code here..."
                  style={{ color: 'transparent' }}
                />
                <Highlight
                  theme={themes.github}
                  code={cell.content || " "}
                  language="python"
                >
                  {({ className, style, tokens, getLineProps, getTokenProps }) => (
                    <pre className={`${className} min-h-[120px] font-mono text-sm bg-slate-50 dark:bg-slate-900 p-3 rounded-md font-medium`} style={style}>
                      {tokens.map((line, i) => (
                        <div key={i} {...getLineProps({ line })}>
                          {line.map((token, key) => (
                            <span key={key} {...getTokenProps({ token })} />
                          ))}
                        </div>
                      ))}
                    </pre>
                  )}
                </Highlight>
              </div>
            </div>

            {isRunning ? (
              <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-md">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running code...
                </div>
              </div>
            ) : cell.output && (
              <div className="bg-slate-100 dark:bg-slate-800 p-3 rounded-md">
                <div className="text-xs text-muted-foreground mb-1">Output:</div>
                <pre className="text-sm font-mono whitespace-pre-wrap">{cell.output}</pre>
              </div>
            )}
          </div>
        )}
      </div>

      {isSelected && (
        <div className="border-t p-2 bg-muted/20">
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); onAddCell("code") }}>
              <Plus className="w-3 h-3 mr-1" />
              Code
            </Button>
            <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); onAddCell("markdown") }}>
              <Plus className="w-3 h-3 mr-1" />
              Markdown
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
} 