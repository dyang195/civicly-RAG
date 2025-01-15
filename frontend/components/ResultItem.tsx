import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { SearchResult } from '../app/types'

interface ResultItemProps {
  result: SearchResult
}

export default function ResultItem({ result }: ResultItemProps) {
  const formattedDate = new Date(result.meeting_date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <Link
      href={`https://councildataproject.org/seattle/#/events/${result.event_id}`}
      target="_blank"
      rel="noopener noreferrer"
      className="block mb-3" // Add margin to the Link wrapper
    >
      <Card className="hover:bg-gray-50 transition-colors cursor-pointer">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold text-gray-900">
            {result.meeting_title}
          </CardTitle>
          <p className="text-sm font-medium text-gray-600">{formattedDate}</p>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700">
            <span className="text-gray-400">...</span>
            &ldquo;{result.text}&rdquo;
            <span className="text-gray-400">...</span>
          </p>
        </CardContent>
      </Card>
    </Link>
  )
}

