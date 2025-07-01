export interface FilterState {
  missionName: string
  missionTypes: string[]
  launchDate: string
  landingDate: string
  dataTimestampBefore: string
  dataTimestampAfter: string
  isUpcoming: boolean | null
  target: string
  objectiveKeywords: string
  subtitleKeywords: string
  partners: string[]
  hasNewsStories: boolean | null
  newsStoriesCountMin: number
  newsStoriesCountMax: number
  paragraphContent: string
  scrapeDateFrom: string
  scrapeDateTo: string
}
