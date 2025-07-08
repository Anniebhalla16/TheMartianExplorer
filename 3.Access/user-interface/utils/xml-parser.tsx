import type { Mission, Story } from "@/types/mission"

export function parseXMLResponse(xmlText: string): Mission[] {
  const parser = new DOMParser()
  const xmlDoc = parser.parseFromString(xmlText, "application/xml")

  const parserError = xmlDoc.querySelector("parsererror")
  if (parserError) {
    throw new Error("XML parsing error: " + parserError.textContent)
  }

  const missions: Mission[] = []
  const missionElements = xmlDoc.querySelectorAll("mission")

  missionElements.forEach((missionEl, index) => {
    const id = getTextContent(missionEl, "title") || `mission-${index}`
    const title = getTextContent(missionEl, "title") || "Untitled Mission"
    const url = getTextContent(missionEl, "url") || ""
    const subtitle = getTextContent(missionEl, "subtitle") || ""
    const dataTimestamp = getTextContent(missionEl, "date") || ""
    const storiesPageUrl = getTextContent(missionEl, "stories_page_url") || ""
    const objective = getMetadataValue(missionEl, "Objective") || ""
    const type = getMetadataValue(missionEl, "Type") || ""
    const target = getMetadataValue(missionEl, "Target") || ""

    const paragraphs = Array.from(
      missionEl.querySelectorAll("paragraph")
    ).map(p => p.textContent || "")

    // parse stories array
    const stories: Story[] = Array.from(
      missionEl.querySelectorAll("stories > story")
    ).map((storyEl, storyIndex) => ({
      id: `${getTextContent(missionEl, "title")}-${storyIndex}`,
      title: getTextContent(storyEl, "title") || "",
      url: getTextContent(storyEl, "url") || "",
      type: getTextContent(storyEl, "type") || "",
      storyImageUrl: getTextContent(storyEl, "story_image_url") || "",
    }))

    const mission: Mission = {
      id,
      title,
      url,
      subtitle,
      type,
      target,
      dataTimestamp,
      objective,
      storiesPageUrl,
      newsStoriesCount: stories.length,
      paragraphs,
      stories,
    }

    missions.push(mission)
  })

  return missions
}

function getTextContent(element: Element, selector: string): string | null {
  const found = element.querySelector(selector)
  return found ? found.textContent?.trim() || null : null
}
function getMetadataValue(element: Element, key: string): string | null {
  const items = element.querySelectorAll("metadata_table > metadata")
  for (const metadata of Array.from(items)) {
    const keyEl = metadata.querySelector("key")
    if (keyEl?.textContent?.trim() === key) {
      return metadata.querySelector("value")?.textContent?.trim() || null
    }
  }
  return null
}
