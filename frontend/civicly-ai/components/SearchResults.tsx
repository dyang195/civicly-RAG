import { useState } from 'react'
import { Button } from '@/components/ui/button'
import ResultItem from './ResultItem'
import { SearchResult } from '../app/types'

interface SearchResultsProps {
  results: SearchResult[]
  totalResults: number
}

export default function SearchResults({ results, totalResults }: SearchResultsProps) {
  const [displayCount, setDisplayCount] = useState(3)

  const displayedResults = results.slice(0, displayCount)

  if (results.length === 0) {
    return (
      <div className="text-center text-gray-600">
        No results found. Please try a different search query.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {displayedResults.map((result) => (
          <ResultItem key={result.event_id} result={result} />
        ))}
      </div>
      {displayCount < totalResults && (
        <div className="flex justify-center mt-4">
          <Button 
            onClick={() => setDisplayCount(Math.min(displayCount + 3, totalResults))} 
            className="px-6"
          >
            Show More Results
          </Button>
        </div>
      )}
    </div>
  )
}

