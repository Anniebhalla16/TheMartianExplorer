"use client"

import { useState, useEffect, useCallback } from "react"
import type { FilterState } from "@/types/filters"
import type { Mission } from "@/types/mission"
import { buildXQuery } from "@/utils/xquery-builder"
import { parseXMLResponse } from "@/utils/xml-parser"

interface UseMissionsResult {
  missions: Mission[]
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useMissions(filters: FilterState): UseMissionsResult {
  const [missions, setMissions] = useState<Mission[]>([])
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
    loading,
    error,
    refetch: fetchMissions,
  }
}
