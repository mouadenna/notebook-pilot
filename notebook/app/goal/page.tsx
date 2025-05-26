"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Target, Sparkles } from "lucide-react"
import { FileUpload } from "@/components/notebook/FileUpload"
import { GenerationOverlay } from "@/components/notebook/GenerationOverlay"
import { useFileUpload } from "@/hooks/useFileUpload"

export default function GoalPage() {
  const router = useRouter()
  const [goal, setGoal] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generationStep, setGenerationStep] = useState("")
  const {
    uploadedFiles,
    isDragOver,
    handleFileUpload,
    handleDrop,
    handleDragOver,
    handleDragLeave,
    removeFile,
  } = useFileUpload()

  const generateNotebook = async () => {
    setIsGenerating(true)
    setGenerationProgress(0)

    const steps = [
      { text: "Analyzing your goal...", duration: 800 },
      { text: "Processing uploaded files...", duration: 600 },
      { text: "Generating notebook structure...", duration: 700 },
      { text: "Creating initial cells...", duration: 500 },
      { text: "Finalizing notebook...", duration: 400 },
    ]

    for (let i = 0; i < steps.length; i++) {
      setGenerationStep(steps[i].text)

      // Animate progress for this step
      const stepProgress = ((i + 1) / steps.length) * 100
      const startProgress = (i / steps.length) * 100

      // Smooth progress animation
      const animateProgress = () => {
        const duration = steps[i].duration
        const startTime = Date.now()

        const updateProgress = () => {
          const elapsed = Date.now() - startTime
          const progress = Math.min(elapsed / duration, 1)
          const currentProgress = startProgress + (stepProgress - startProgress) * progress

          setGenerationProgress(currentProgress)

          if (progress < 1) {
            requestAnimationFrame(updateProgress)
          }
        }

        updateProgress()
      }

      animateProgress()
      await new Promise((resolve) => setTimeout(resolve, steps[i].duration))
    }

    // Complete the generation
    setGenerationProgress(100)
    await new Promise((resolve) => setTimeout(resolve, 300))

    // Navigate to notebook page with initial data
    router.push("/notebook")
  }

  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 p-8 text-center">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Target className="w-10 h-10 text-blue-600" />
          <h1 className="text-4xl font-bold text-gray-900">Create Your Notebook</h1>
        </div>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Define your project goal and upload relevant files to generate a structured notebook tailored to your needs
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex gap-8 p-8 pt-0 overflow-hidden">
        {/* Left Section - Goal Input */}
        <div className="flex-1 flex flex-col">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Project Goal</h2>
            <p className="text-gray-600">Describe what you want to achieve with this notebook</p>
          </div>

          <div className="flex-1 flex flex-col">
            <div className="relative flex-1">
              <Textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="Example: Analyze customer purchase patterns to identify trends and predict future buying behavior using sales data from the past year..."
                className="h-full text-base leading-relaxed resize-none border-2 focus:border-blue-500 transition-colors"
              />
              <div className="absolute bottom-2 right-2 text-sm text-gray-500 bg-white/80 px-2 py-1 rounded">
                {goal.length} characters
              </div>
            </div>
          </div>
        </div>

        {/* Right Section - File Upload */}
        <div className="flex-1 flex flex-col">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Project Files</h2>
            <p className="text-gray-600">Upload datasets, images, or other files for your analysis</p>
          </div>

          <FileUpload
            uploadedFiles={uploadedFiles}
            isDragOver={isDragOver}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onFileUpload={handleFileUpload}
            onRemoveFile={removeFile}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="flex-shrink-0 p-8 pt-0">
        {!isGenerating && (
          <div className="flex flex-col items-center">
            <Button
              onClick={generateNotebook}
              disabled={!goal.trim()}
              size="lg"
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 text-lg font-semibold transform transition-all duration-200 hover:scale-105 hover:shadow-lg"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Generate Notebook
            </Button>
            <p className="text-center text-gray-500 text-sm mt-3 min-h-[20px]">
              {!goal.trim() ? "Please enter a project goal to continue" : ""}
            </p>
          </div>
        )}
      </div>

      {/* Generation Overlay */}
      {isGenerating && (
        <GenerationOverlay
          generationStep={generationStep}
          generationProgress={generationProgress}
        />
      )}
    </div>
  )
} 