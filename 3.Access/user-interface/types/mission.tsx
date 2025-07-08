export interface Story {
  id: string
  title: string
  url: string
  type: string
  storyImageUrl: string
}

export interface Mission {
  id: string
  title: string
  url: string
  subtitle: string
  type: string
  target: string
  dataTimestamp: string
  objective: string
  storiesPageUrl: string
  newsStoriesCount: number
  paragraphs: string[]
  stories: Story[]
}