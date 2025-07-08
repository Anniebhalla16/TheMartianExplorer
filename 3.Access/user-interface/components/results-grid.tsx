"use client"

import type { Mission, Story } from "@/types/mission"
import { MissionCard } from "./mission-card"
import { StoryCard } from "./story-card"

interface ResultsGridProps {
  stories: Story[]
  missions: Mission[]
  loading: boolean
  error: string | null
  onRefresh: () => void
}

export function ResultsGrid({ missions, stories, loading, error, onRefresh }: ResultsGridProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading missions...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Missions</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={onRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (missions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Missions Found</h3>
          <p className="text-gray-600">Try adjusting your filters to see more results.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Mission Results ({missions.length})</h2>
          <button onClick={onRefresh} className="text-sm text-blue-600 hover:text-blue-800 flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {missions.map((mission) => (
          <MissionCard key={mission.id} mission={mission} />
        ))}
        {stories.map((story)=>(
          <StoryCard key={story.id} story={story}/>
        ))}
      </div>


    </div>
  )
}
