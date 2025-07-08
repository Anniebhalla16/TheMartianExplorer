import type { Mission } from "@/types/mission"

interface MissionCardProps {
  mission: Mission
}

export function MissionCard({ mission }: MissionCardProps) {
  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A"
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return dateString
    }
  }

const getTypeColor = (type: string) => {
  const t = type.toLowerCase()

  if (t.includes("orbiter")) {
    return "bg-blue-100 text-blue-800"
  }
  if (t.includes("lander")) {
    return "bg-green-100 text-green-800"
  }
  if (t.includes("rover")) {
    return "bg-purple-100 text-purple-800"
  }
  if (t.includes("flyby")) {
    return "bg-yellow-100 text-yellow-800"
  }
  if (t.includes("sample return")) {
    return "bg-red-100 text-red-800"
  }
  return "bg-gray-100 text-gray-800"
}

  return (
    <a href={mission.url} target="_blank" className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">{mission.title}</h3>
          {mission.type && (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(mission.type)}`}>
              {mission.type}
            </span>
          )}
        </div>

        {mission.subtitle && <p className="text-gray-600 text-sm mb-4 line-clamp-2">{mission.subtitle}</p>}

        <div className="space-y-2 text-sm text-gray-500">
          {mission.target && (
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span>Target: {mission.target}</span>
            </div>
          )}
        </div>

        {mission.newsStoriesCount > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center text-sm text-blue-600">
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
                />
              </svg>
              <span>{mission.newsStoriesCount} news stories</span>
            </div>
          </div>
        )}

        {mission.dataTimestamp && (
          <div className="mt-2 text-xs text-gray-400">Data updated: {formatDate(mission.dataTimestamp)}</div>
        )}
      </div>
    </a>
  )
}
