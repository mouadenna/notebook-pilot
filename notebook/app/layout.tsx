import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { NotebookProvider } from "@/contexts/NotebookContext"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Notebook Pilot",
  description: "An interactive notebook for data analysis and exploration",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <NotebookProvider>{children}</NotebookProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
