'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Header from '../components/Header'
import SearchBox from '../components/SearchBox'
import SearchResults from '../components/SearchResults'
import { SearchResponse } from './types'

export default function Home() {
  const [searchPerformed, setSearchPerformed] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (query: string, startDate: string, endDate: string) => {
    setSearchPerformed(true)
    setIsLoading(true)
    setError(null)
    setSearchResults(null)
    
    try {
      const payload: any = {
        query,
        limit: 10
      }
  
      if (startDate) {
        payload.start_date = startDate
      }
      if (endDate) {
        payload.end_date = endDate
      }
  
      const response = await fetch('http://localhost:8000/search', {
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
          animate={{ y: searchPerformed ? 0 : '35vh' }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto space-y-3"
        >
          {!searchPerformed && (
            <p className="text-gray-600 text-center">
              Search Seattle City Council meeting transcripts by typing your query below
            </p>
          )}
          <SearchBox onSearch={handleSearch} />
        </motion.div>
        {isLoading && (
          <div className="mt-6 text-center">
            <p>Loading results...</p>
          </div>
        )}
        {error && (
          <div className="mt-6 text-center text-red-500">
            <p>{error}</p>
          </div>
        )}
        {searchResults && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-6 max-w-3xl mx-auto"
          >
            <SearchResults results={searchResults.results} totalResults={searchResults.total_results} />
          </motion.div>
        )}
      </main>
    </div>
  )
}

