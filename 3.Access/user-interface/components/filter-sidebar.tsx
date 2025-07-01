"use client"

import { useState } from "react"
import type { FilterState } from "@/types/filters"

interface FilterSidebarProps {
  filters: FilterState
  onFilterChange: (filters: Partial<FilterState>) => void
  onClearFilters: () => void
  loading: boolean
}

export function FilterSidebar({ filters, onFilterChange, onClearFilters, loading }: FilterSidebarProps) {
  const [availableOptions, setAvailableOptions] = useState({
    missionTypes: ["Orbiter", "Lander", "Rover", "Flyby", "Sample Return"],
    targets: ["Mars", "Phobos", "Deimos", "Mars Orbit"],
    partners: ["NASA", "ESA", "Roscosmos", "JAXA", "ISRO", "CNSA"],
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
          disabled={loading}
        />
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

      {/* Launch & Landing Dates */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Launch Date</label>
          <input
            type="date"
            value={filters.launchDate}
            onChange={(e) => onFilterChange({ launchDate: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Landing Date</label>
          <input
            type="date"
            value={filters.landingDate}
            onChange={(e) => onFilterChange({ landingDate: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
        </div>
      </div>

      {/* Data Timestamp */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Data Timestamp</label>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input
              type="date"
              value={filters.dataTimestampAfter}
              onChange={(e) => onFilterChange({ dataTimestampAfter: e.target.value })}
              placeholder="After"
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <input
              type="date"
              value={filters.dataTimestampBefore}
              onChange={(e) => onFilterChange({ dataTimestampBefore: e.target.value })}
              placeholder="Before"
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
          </div>
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="timeframe"
                checked={filters.isUpcoming === true}
                onChange={() => onFilterChange({ isUpcoming: true })}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">Upcoming</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="timeframe"
                checked={filters.isUpcoming === false}
                onChange={() => onFilterChange({ isUpcoming: false })}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">Historical</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="timeframe"
                checked={filters.isUpcoming === null}
                onChange={() => onFilterChange({ isUpcoming: null })}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">All</span>
            </label>
          </div>
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
          disabled={loading}
        />
      </div>

      {/* Subtitle Keywords */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Subtitle Keywords</label>
        <input
          type="text"
          value={filters.subtitleKeywords}
          onChange={(e) => onFilterChange({ subtitleKeywords: e.target.value })}
          placeholder="Search subtitles..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
      </div>

      {/* Partner/Agency */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Partner / Agency</label>
        <div className="space-y-2">
          {availableOptions.partners.map((partner) => (
            <label key={partner} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.partners.includes(partner)}
                onChange={(e) => {
                  const newPartners = e.target.checked
                    ? [...filters.partners, partner]
                    : filters.partners.filter((p) => p !== partner)
                  onFilterChange({ partners: newPartners })
                }}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-sm text-gray-700">{partner}</span>
            </label>
          ))}
        </div>
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

      {/* News Stories Count Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          News Stories Count: {filters.newsStoriesCountMin} - {filters.newsStoriesCountMax}
        </label>
        <div className="grid grid-cols-2 gap-3">
          <input
            type="range"
            min="0"
            max="100"
            value={filters.newsStoriesCountMin}
            onChange={(e) => onFilterChange({ newsStoriesCountMin: Number.parseInt(e.target.value) })}
            className="w-full"
            disabled={loading}
          />
          <input
            type="range"
            min="0"
            max="100"
            value={filters.newsStoriesCountMax}
            onChange={(e) => onFilterChange({ newsStoriesCountMax: Number.parseInt(e.target.value) })}
            className="w-full"
            disabled={loading}
          />
        </div>
      </div>

      {/* Paragraph Content */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Paragraph Content</label>
        <input
          type="text"
          value={filters.paragraphContent}
          onChange={(e) => onFilterChange({ paragraphContent: e.target.value })}
          placeholder="Search paragraph content..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
      </div>

      {/* Scrape Date Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Scrape Date Range</label>
        <div className="grid grid-cols-2 gap-3">
          <input
            type="date"
            value={filters.scrapeDateFrom}
            onChange={(e) => onFilterChange({ scrapeDateFrom: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <input
            type="date"
            value={filters.scrapeDateTo}
            onChange={(e) => onFilterChange({ scrapeDateTo: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
        </div>
      </div>
    </div>
  )
}
