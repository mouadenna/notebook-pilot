import { Sparkles } from "lucide-react"

interface GenerationOverlayProps {
  generationStep: string
  generationProgress: number
}

export function GenerationOverlay({ generationStep, generationProgress }: GenerationOverlayProps) {
  return (
    <div className="fixed inset-0 bg-white z-50 flex items-center justify-center">
      <div className="max-w-2xl w-full px-8">
        {/* Generation Progress */}
        <div className="text-center">
          <div className="relative inline-flex items-center justify-center w-24 h-24 mb-8">
            <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
            <div
              className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"
              style={{ animationDuration: "1s" }}
            ></div>
            <Sparkles className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-4">Generating Your Notebook</h3>
          <p className="text-xl text-gray-600 mb-8">{generationStep}</p>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-lg text-gray-600 mb-3">
              <span>Progress</span>
              <span>{Math.round(generationProgress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${generationProgress}%` }}
              ></div>
            </div>
          </div>

          {/* Animated Dots */}
          <div className="flex justify-center space-x-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"
                style={{
                  animationDelay: `${i * 0.2}s`,
                  animationDuration: "1s",
                }}
              ></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 