'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Header from '../components/Header'
import SearchBox from '../components/SearchBox'
import SearchResults from '../components/SearchResults'
import LoadingDots from '../components/LoadingDots'
import SummaryResult from '../components/SummaryResult'
import { SearchResponse } from './types'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function Home() {
  const [searchPerformed, setSearchPerformed] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedCity, setSelectedCity] = useState("seattle")

  const handleSearch = async (query: string, startDate: string, endDate: string) => {
    setSearchPerformed(true)
    setIsLoading(true)
    setError(null)
    setSearchResults(null)

    try {
      const payload: {
        query: string;
        limit: number;
        start_date?: string;
        end_date?: string;
      } = {
        query,
        limit: 10
      }
  
      if (startDate) {
        payload.start_date = startDate
      }
      if (endDate) {
        payload.end_date = endDate
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/search'

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
  

      if (!response.ok) {
        throw new Error('Failed to fetch search results')
      }

      const data: SearchResponse = await response.json()
      setSearchResults(data)
    } catch (err) {
      setError('An error occurred while fetching search results. Please try again.')
      console.error('Search error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="p-4">
        <motion.div
          initial={{ y: searchPerformed ? -50 : 0 }}
          animate={{ y: searchPerformed ? 0 : '20vh' }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto space-y-6"
        >
          {!searchPerformed && (
            <div className="text-center space-y-4">
              <h1 className="text-5xl text-gray-900">Know your city</h1>
              <h2 className="text-3xl text-gray-700">Engage with your community</h2>
              <p className="text-2xl text-gray-600 flex flex-wrap items-center justify-center gap-2">
                Search
                <Select value={selectedCity} onValueChange={setSelectedCity}>
                  <SelectTrigger className="mx-2 w-[120px] h-auto py-0.5 px-2 text-2xl text-gray-600 bg-transparent hover:bg-transparent focus:ring-0 inline-flex items-center border border-gray-200 rounded-md [&>svg]:ml-1 [&>svg]:border-l [&>svg]:border-gray-200 [&>svg]:pl-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="seattle">Seattle</SelectItem>
                    <SelectItem value="coming-soon" disabled>
                      More cities coming soon
                    </SelectItem>
                  </SelectContent>
                </Select>
                City Council Records
              </p>
            </div>
          )}
          <SearchBox onSearch={handleSearch} />
        </motion.div>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="mt-6 text-center"
          >
            <p className="text-xl text-gray-600">
              Searching through records<LoadingDots />
            </p>
          </motion.div>
        )}
        {error && (
          <div className="mt-6 text-center text-red-500">
            <p>{error}</p>
          </div>
        )}
        {searchResults && !isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 max-w-3xl mx-auto space-y-10"
          >
            <SummaryResult summary={searchResults.summary} />
            <SearchResults results={searchResults.results} totalResults={searchResults.total_results} />
          </motion.div>
        )}
      </main>
    </div>
  )
}

