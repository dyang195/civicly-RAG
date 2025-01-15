export interface SearchResult {
  event_id: string
  text: string
  meeting_date: string
  meeting_title: string
  speaker: string
  relevance_score: number
  start_time: string
  end_time: string
}

export interface SearchResponse {
  results: SearchResult[]
  total_results: number
  processing_time: number
  summary: string
}

export type City = "seattle" | "coming-soon"
