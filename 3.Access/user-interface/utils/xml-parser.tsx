import type { Mission } from "@/types/mission"

export function parseXMLResponse(xmlText: string): Mission[] {
  try {
    const parser = new DOMParser()
    const xmlDoc = parser.parseFromString(xmlText, "application/xml")

    const parserError = xmlDoc.querySelector("parsererror")
    if (parserError) {
      throw new Error("XML parsing error: " + parserError.textContent)
    }

    const missions: Mission[] = []
    const missionElements = xmlDoc.querySelectorAll("mission")

    missionElements.forEach((missionEl, index) => {
      const mission: Mission = {
        id: missionEl.getAttribute("id") || `mission-${index}`,
        title: getTextContent(missionEl, "title") || "Untitled Mission",
        url: getTextContent(missionEl, "url") || "",
        subtitle: getTextContent(missionEl, "subtitle") || "",
        type: getMetadataValue(missionEl, "Type") || "",
        target: getMetadataValue(missionEl, "Target") || "",
        launchDate: extractDateFromLaunchLanding(getMetadataValue(missionEl, "Launch / Landing"), "launch") || "",
        landingDate: extractDateFromLaunchLanding(getMetadataValue(missionEl, "Launch / Landing"), "landing") || "",
        dataTimestamp: getTextContent(missionEl, "date") || "",
        objective: getMetadataValue(missionEl, "Objective") || "",
        partners: getMetadataValues(missionEl, "partner"),
        newsStoriesCount: missionEl.querySelectorAll("stories story").length,
        paragraphs: Array.from(missionEl.querySelectorAll("paragraph")).map((p) => p.textContent || ""),
      }

      missions.push(mission)
    })

    return missions
  } catch (error) {
    console.error("Error parsing XML:", error)
    throw new Error("Failed to parse mission data")
  }
}

function getTextContent(element: Element, selector: string): string | null {
  const found = element.querySelector(selector)
  return found ? found.textContent?.trim() || null : null
}

function getMetadataValue(element: Element, key: string): string | null {
  const metadata = element.querySelector(`metadata_table metadata[key="${key}"] value`)
  return metadata ? metadata.textContent?.trim() || null : null
}

function getMetadataValues(element: Element, key: string): string[] {
  const metadataElements = element.querySelectorAll(`metadata_table metadata[key="${key}"] value`)
  return Array.from(metadataElements)
    .map((el) => el.textContent?.trim() || "")
    .filter(Boolean)
}

function extractDateFromLaunchLanding(launchLandingText: string | null, type: "launch" | "landing"): string | null {
  if (!launchLandingText) return null

  const regex =
    type === "launch" ? /Launch:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i : /Landing:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i

  const match = launchLandingText.match(regex)
  return match ? match[1] : null
}
