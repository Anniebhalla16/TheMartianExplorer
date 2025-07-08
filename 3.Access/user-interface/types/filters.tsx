export interface FilterState {
  missionName: string
  missionTypes: string[]
  articlePublishedFrom: string
  articlePublishedTo: string
  target: string
  missionStatus : string[]
  objectiveKeywords: string
  subtitleKeywords: string
  hasNewsStories: boolean | null
  paragraphContent: string
  viewStories: boolean    
}
