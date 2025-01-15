'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Calendar } from '@/components/ui/calendar'
import { FilterIcon } from 'lucide-react'
import { format, isValid, parse } from 'date-fns'

interface SearchBoxProps {
  onSearch: (query: string, startDate: string, endDate: string) => void
}

export default function SearchBox({ onSearch }: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [dateError, setDateError] = useState<string | null>(null)

  const validateAndFormatDate = (dateStr: string): string => {
    if (!dateStr) return ''

    // Check if the date is in MM/DD/YYYY format
    const parsed = parse(dateStr, 'MM/dd/yyyy', new Date())
    if (!isValid(parsed)) {
      return ''
    }
    return format(parsed, 'MM/dd/yyyy')
  }

  const handleDateChange = (field: 'start' | 'end', value: string) => {
    setDateError(null)
    const formatted = validateAndFormatDate(value)
    
    if (value && !formatted) {
      setDateError('Please enter date in MM/DD/YYYY format')
      if (field === 'start') setStartDate(value)
      else setEndDate(value)
      return
    }

    if (field === 'start') {
      setStartDate(value)
      if (formatted && endDate) {
        const start = parse(formatted, 'MM/dd/yyyy', new Date())
        const end = parse(endDate, 'MM/dd/yyyy', new Date())
        if (start > end) {
          setDateError('Start date cannot be after end date')
        }
      }
    } else {
      setEndDate(value)
      if (formatted && startDate) {
        const start = parse(startDate, 'MM/dd/yyyy', new Date())
        const end = parse(formatted, 'MM/dd/yyyy', new Date())
        if (end < start) {
          setDateError('End date cannot be before start date')
        }
      }
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (dateError) return

    const formattedStartDate = validateAndFormatDate(startDate)
    const formattedEndDate = validateAndFormatDate(endDate)

    if ((startDate && !formattedStartDate) || (endDate && !formattedEndDate)) {
      setDateError('Please enter valid dates in MM/DD/YYYY format')
      return
    }

    onSearch(query, formattedStartDate, formattedEndDate)
    setIsFilterOpen(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-md shadow-sm">
      <div className="flex items-center space-x-2">
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='Try "bike lanes" or "climate action in my area"'
          className="flex-grow"
          required
        />
        <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" size="icon">
              <FilterIcon className="h-4 w-4" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-64 p-3">
            <div className="space-y-3">
              <div>
                <Label htmlFor="startDate">Start Date</Label>
                <div className="flex items-center mt-1">
                  <Input
                    type="text"
                    id="startDate"
                    value={startDate}
                    onChange={(e) => handleDateChange('start', e.target.value)}
                    placeholder="MM/DD/YYYY"
                    className="flex-grow"
                  />
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="ghost" size="icon" className="ml-1">
                        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                          <line x1="16" y1="2" x2="16" y2="6" />
                          <line x1="8" y1="2" x2="8" y2="6" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={startDate ? parse(startDate, 'MM/dd/yyyy', new Date()) : undefined}
                        onSelect={(date) => handleDateChange('start', date ? format(date, 'MM/dd/yyyy') : '')}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>
              <div>
                <Label htmlFor="endDate">End Date</Label>
                <div className="flex items-center mt-1">
                  <Input
                    type="text"
                    id="endDate"
                    value={endDate}
                    onChange={(e) => handleDateChange('end', e.target.value)}
                    placeholder="MM/DD/YYYY"
                    className="flex-grow"
                  />
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="ghost" size="icon" className="ml-1">
                        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                          <line x1="16" y1="2" x2="16" y2="6" />
                          <line x1="8" y1="2" x2="8" y2="6" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={endDate ? parse(endDate, 'MM/dd/yyyy', new Date()) : undefined}
                        onSelect={(date) => handleDateChange('end', date ? format(date, 'MM/dd/yyyy') : '')}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>
              {dateError && (
                <p className="text-sm text-red-500 mt-2">{dateError}</p>
              )}
            </div>
          </PopoverContent>
        </Popover>
        <Button type="submit">Search</Button>
      </div>
      {(startDate || endDate) && !dateError && (
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

