"use client"

import type { FilterState } from "@/types/filters"
import { useState } from "react"

interface FilterSidebarProps {
  filters: FilterState
  onFilterChange: (filters: Partial<FilterState>) => void
  onClearFilters: () => void
  loading: boolean
}

export function FilterSidebar({ filters, onFilterChange, onClearFilters, loading }: FilterSidebarProps) {
  const [availableOptions, setAvailableOptions] = useState({
    missionTypes: ["Orbiter", "Lander", "Rover", "Sample Return", "Flyby"],
    targets: ["Mars", "Phobos", "Deimos", "Mars Orbit" , "Jezero Crater, Mars"],
    status: ["past", "active", "future", "all"]

  })

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        <button onClick={onClearFilters} className="text-sm text-blue-600 hover:text-blue-800" disabled={loading}>
          Clear All
        </button>
      </div>

      {/* Mission Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Mission Name</label>
        <input
          type="text"
          value={filters.missionName}
          onChange={(e) => onFilterChange({ missionName: e.target.value })}
          placeholder="Search mission names..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          // disabled={loading}
        />
      </div>

{/* View Stories */}
 <div>
   <label className="flex items-center">
     <input
       type="checkbox"
       checked={filters.viewStories}
       onChange={(e) => onFilterChange({ viewStories: e.target.checked })}
       className="mr-2"
       disabled={loading}
     />
     <span className="text-sm font-medium text-gray-700">View Stories</span>
   </label>
 </div>

      {/* Mission Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Mission Type</label>
        <div className="space-y-2">
          {availableOptions.missionTypes.map((type) => (
            <label key={type} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.missionTypes.includes(type)}
                onChange={(e) => {
                  const newTypes = e.target.checked
                    ? [...filters.missionTypes, type]
                    : filters.missionTypes.filter((t) => t !== type)
                  onFilterChange({ missionTypes: newTypes })
                }}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">{type}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Article Published Date */}
      <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Article Published
      </label>
      <div className="flex flex-col items-center space-x-2">
        <input
          type="date"
          value={filters.articlePublishedFrom}
          onChange={(e) => onFilterChange({ articlePublishedFrom: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <span className="text-gray-500">to</span>
        <input
          type="date"
          value={filters.articlePublishedTo}
          onChange={(e) => onFilterChange({ articlePublishedTo: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
      </div>
    </div>

    {/* Mission Status */}
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Mission Status
      </label>
      <div className="space-y-2">
        {availableOptions.status.map((status) => (
          <label key={status} className="flex items-center">
            <input
              type="checkbox"
              checked={filters.missionStatus.includes(status)}
              onChange={(e) => {
                let newStatuses = filters.missionStatus.includes(status)
                  ? filters.missionStatus.filter((s) => s !== status)
                  : [...filters.missionStatus, status]

                if (status === "all" && e.target.checked) {
                  newStatuses = ["all"]
                } else if (status !== "all" && e.target.checked) {
                  newStatuses = newStatuses.filter((s) => s !== "all")
                }

                onFilterChange({ missionStatus: newStatuses })
              }}
              className="mr-2"
              disabled={loading}
            />
            <span className="text-sm text-gray-700">
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
          </label>
        ))}
      </div>
    </div>



      {/* Target */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Target</label>
        <select
          value={filters.target}
          onChange={(e) => onFilterChange({ target: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        >
          <option value="">All Targets</option>
          {availableOptions.targets.map((target) => (
            <option key={target} value={target}>
              {target}
            </option>
          ))}
        </select>
      </div>

      {/* Objective Keywords */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Objective Keywords</label>
        <input
          type="text"
          value={filters.objectiveKeywords}
          onChange={(e) => onFilterChange({ objectiveKeywords: e.target.value })}
          placeholder="Search objectives..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          // disabled={loading}
        />
      </div>

      {/* Has News Stories */}
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={filters.hasNewsStories === true}
            onChange={(e) => onFilterChange({ hasNewsStories: e.target.checked ? true : null })}
            className="mr-2"
            disabled={loading}
          />
          <span className="text-sm font-medium text-gray-700">Has News Stories</span>
        </label>
      </div>
    </div>
  )
}
