"use client"

import type { FilterState } from "@/types/filters"
import { Story, type Mission } from "@/types/mission"
import { parseXMLResponse } from "@/utils/xml-parser"
import { buildXQuery } from "@/utils/xquery-builder"
import { useCallback, useEffect, useState } from "react"

interface UseMissionsResult {
  missions: Mission[]
  stories: Story[]
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useMissions(filters: FilterState): UseMissionsResult {
  const [missions, setMissions] = useState<Mission[]>([])
  const [stories, setStories] = useState<Story[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMissions = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const xquery = buildXQuery(filters)
      const encodedQuery = encodeURIComponent(xquery)

      const response = await fetch(`/api/missions?query=${encodedQuery}&howmany=-1`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const xmlText = await response.text()
      const parsedMissions = parseXMLResponse(xmlText)
      
      setMissions(parsedMissions)
      
      const allStories = parsedMissions.flatMap((m) => m.stories)
      setStories(allStories)

      console.log(parsedMissions)

    } catch (err) {
      console.error("Error fetching missions:", err)
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchMissions()
  }, [fetchMissions])

  return {
    missions,
    stories,
    loading,
    error,
    refetch: fetchMissions,
  }
}
