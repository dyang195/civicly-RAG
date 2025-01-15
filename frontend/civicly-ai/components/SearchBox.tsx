'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { CalendarIcon, FilterIcon } from 'lucide-react'
import { format } from 'date-fns'

interface SearchBoxProps {
  onSearch: (query: string, startDate: string, endDate: string) => void
}

export default function SearchBox({ onSearch }: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(query, startDate, endDate)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg">
      <div className="flex items-center space-x-2">
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query"
          className="flex-grow"
          required
        />
        <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" size="icon">
              <FilterIcon className="h-4 w-4" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80 p-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="startDate">Start Date</Label>
                <div className="flex items-center mt-1">
                  <Input
                    type="date"
                    id="startDate"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="flex-grow"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="endDate">End Date</Label>
                <div className="flex items-center mt-1">
                  <Input
                    type="date"
                    id="endDate"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="flex-grow"
                  />
                </div>
              </div>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full">
                    <CalendarIcon className="h-4 w-4 mr-2" />
                    Open Calendar
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="range"
                    selected={{ from: startDate ? new Date(startDate) : undefined, to: endDate ? new Date(endDate) : undefined }}
                    onSelect={(range) => {
                      setStartDate(range?.from ? format(range.from, 'yyyy-MM-dd') : '')
                      setEndDate(range?.to ? format(range.to, 'yyyy-MM-dd') : '')
                    }}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </PopoverContent>
        </Popover>
        <Button type="submit">Search</Button>
      </div>
      {(startDate || endDate) && (
        <div className="text-sm text-gray-500">
          {startDate && (
            <span className="mr-2">
              From: {startDate}
            </span>
          )}
          {endDate && (
            <span>
              To: {endDate}
            </span>
          )}
        </div>
      )}
    </form>
  )
}

