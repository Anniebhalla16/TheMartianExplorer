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

  // Upcoming vs Historical toggle
  if (filters.isUpcoming === true) {
    conditions.push(`xs:dateTime(date) gt current-dateTime()`)
  } else if (filters.isUpcoming === false) {
    conditions.push(`xs:dateTime(date) le current-dateTime()`)
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


  // Paragraph Content
  if (filters.paragraphContent.trim()) {
  const kw = filters.paragraphContent.toLowerCase()
  conditions.push(
    `exists(paragraphs/paragraph[contains(lower-case(.), "${kw}")])`
  )
}
  // Build the complete XQuery
  const whereClause = conditions.length > 0 ? `[${conditions.join(" and ")}]` : ""

  return `
    for $mission in //mission${whereClause}
    return $mission
  `.trim()
}
