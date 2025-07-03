"use client"

import { FilterSidebar } from "@/components/filter-sidebar"
import { ResultsGrid } from "@/components/results-grid"
import { useMissions } from "@/hooks/use-missions"
import type { FilterState } from "@/types/filters"
import { useEffect, useState } from "react"

const initialFilters: FilterState = {
  missionName: "",
  missionTypes: [],
  missionStatus: [],
  articlePublishedFrom: "",
  articlePublishedTo: "",
  target: "",
  objectiveKeywords: "",
  subtitleKeywords: "",
  hasNewsStories: null,
  paragraphContent: ""
}

export default function MartianExplorerPage() {
  const [filters, setFilters] = useState<FilterState>(initialFilters)
  const { missions, loading, error, refetch } = useMissions(filters)

  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }))
  }
  useEffect(()=>{
    console.log(filters)
  },[filters])

  const handleClearFilters = () => {
    setFilters(initialFilters)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">The Martian Explorer - Chaos to Cosmos</h1>
          <p className="text-gray-600 mt-2">Explore Mars missions with advanced filtering capabilities</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Filter Sidebar */}
          <div className="w-80 flex-shrink-0">
            <FilterSidebar
              filters={filters}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
              loading={loading}
            />
          </div>

          {/* Results Grid */}
          <div className="flex-1">
            <ResultsGrid missions={missions} loading={loading} error={error} onRefresh={refetch} />
          </div>
        </div>
      </div>
    </div>
  )
}
