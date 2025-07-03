import type { FilterState } from "@/types/filters"

export function buildXQuery(filters: FilterState): string {
  const conditions: string[] = []

    // Mission Name - free-text search on <title>
  if (filters.missionName.trim()) {
    conditions.push(
      `contains(lower-case(title), "${filters.missionName.toLowerCase()}")`
    )
  }
  // Mission Type - substring match on metadata_table/metadata[key='Type']/value
  if (filters.missionTypes.length > 0) {
    const typeConditions = filters.missionTypes
      .map(
        (type) =>
          `contains(lower-case(metadata_table/metadata[key='Type']/value), "${type.toLowerCase()}")`
      )
      .join(" or ")
    conditions.push(`(${typeConditions})`)
  }

  if (filters.missionStatus.length > 0 && !filters.missionStatus.includes("all")) {
    const statusConds = filters.missionStatus
      .map(
        (s) =>
          `string(missions_status) = "${s}"`
      )
      .join(" or ")
    conditions.push(`(${statusConds})`)
  }

 // Mission Article Publish Date Range — compare only the YYYY-MM-DD part
  if (filters.articlePublishedFrom || filters.articlePublishedTo) {
    const pubDateExpr = 
      `xs:date(substring-before(string(date),"T"))`

    if (filters.articlePublishedFrom) {
      conditions.push(
        `${pubDateExpr} >= xs:date("${filters.articlePublishedFrom}")`
      )
    }
    if (filters.articlePublishedTo) {
      conditions.push(
        `${pubDateExpr} <= xs:date("${filters.articlePublishedTo}")`
      )
    }
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
