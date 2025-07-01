import type { FilterState } from "@/types/filters"

export function buildXQuery(filters: FilterState): string {
  const conditions: string[] = []

  // Mission Name - free-text search on <title>
  if (filters.missionName.trim()) {
    conditions.push(`contains(lower-case(title), "${filters.missionName.toLowerCase()}")`)
  }

  // Mission Type - multi-select on metadata_table/metadata[key='Type']/value
  if (filters.missionTypes.length > 0) {
    const typeConditions = filters.missionTypes
      .map((type) => `metadata_table/metadata[key='Type']/value = "${type}"`)
      .join(" or ")
    conditions.push(`(${typeConditions})`)
  }

  // Launch Date - from metadata_table/metadata[key='Launch / Landing']/value
  if (filters.launchDate) {
    conditions.push(`metadata_table/metadata[key='Launch / Landing']/value >= "${filters.launchDate}"`)
  }

  // Landing Date - from metadata_table/metadata[key='Launch / Landing']/value
  if (filters.landingDate) {
    conditions.push(`metadata_table/metadata[key='Launch / Landing']/value <= "${filters.landingDate}"`)
  }

  // Data Timestamp - before/after filter on top-level <date>
  if (filters.dataTimestampAfter) {
    conditions.push(`date >= "${filters.dataTimestampAfter}"`)
  }
  if (filters.dataTimestampBefore) {
    conditions.push(`date <= "${filters.dataTimestampBefore}"`)
  }

  // Upcoming vs Historical toggle
  if (filters.isUpcoming === true) {
    conditions.push(`date > current-date()`)
  } else if (filters.isUpcoming === false) {
    conditions.push(`date <= current-date()`)
  }

  // Target - dropdown on metadata_table/metadata[key='Target']/value
  if (filters.target) {
    conditions.push(`metadata_table/metadata[key='Target']/value = "${filters.target}"`)
  }

  // Objective Keywords - full-text search on <value> where key='Objective'
  if (filters.objectiveKeywords.trim()) {
    conditions.push(
      `contains(lower-case(metadata_table/metadata[key='Objective']/value), "${filters.objectiveKeywords.toLowerCase()}")`,
    )
  }

  // Subtitle Keywords - free-text on <subtitle>
  if (filters.subtitleKeywords.trim()) {
    conditions.push(`contains(lower-case(subtitle), "${filters.subtitleKeywords.toLowerCase()}")`)
  }

  // Partner/Agency - multi-select on metadata_table/metadata[key='partner']/value
  if (filters.partners.length > 0) {
    const partnerConditions = filters.partners
      .map((partner) => `metadata_table/metadata[key='partner']/value = "${partner}"`)
      .join(" or ")
    conditions.push(`(${partnerConditions})`)
  }

  // Has News Stories - checkbox (at least one <stories>/<story>)
  if (filters.hasNewsStories === true) {
    conditions.push(`exists(stories/story)`)
  }

  // News Stories Count - numeric range over count(stories/story)
  if (filters.newsStoriesCountMin > 0) {
    conditions.push(`count(stories/story) >= ${filters.newsStoriesCountMin}`)
  }
  if (filters.newsStoriesCountMax < 100) {
    conditions.push(`count(stories/story) <= ${filters.newsStoriesCountMax}`)
  }

  // Paragraph Content - snippet search across <paragraph> elements
  if (filters.paragraphContent.trim()) {
    conditions.push(`contains(lower-case(paragraph), "${filters.paragraphContent.toLowerCase()}")`)
  }

  // Scrape Date - date-range on <scraped_at>
  if (filters.scrapeDateFrom) {
    conditions.push(`scraped_at >= "${filters.scrapeDateFrom}"`)
  }
  if (filters.scrapeDateTo) {
    conditions.push(`scraped_at <= "${filters.scrapeDateTo}"`)
  }

  // Build the complete XQuery
  const whereClause = conditions.length > 0 ? `[${conditions.join(" and ")}]` : ""

  return `
    for $mission in //mission${whereClause}
    return $mission
  `.trim()
}
