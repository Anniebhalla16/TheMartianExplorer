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
  paragraphContent: string
}
