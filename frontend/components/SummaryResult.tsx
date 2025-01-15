import { Card } from '@/components/ui/card'
import { Bot } from 'lucide-react'

interface SummaryResultProps {
  summary: string
}

export default function SummaryResult({ summary }: SummaryResultProps) {
  return (
    <Card className="mb-8 overflow-hidden">
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200 p-6">
        <div className="flex items-center mb-3">
          <Bot className="w-5 h-5 text-blue-500 mr-2" />
          <span className="text-sm font-medium text-blue-600">AI Summary</span>
        </div>
        <p className="text-gray-800 text-lg leading-relaxed">{summary}</p>
      </div>
    </Card>
  )
}

