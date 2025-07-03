#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth
from lxml import etree

# 1) Configuration
EXIST_REST = "http://localhost:8080/exist/rest/db/martian-explorer/missions.xml"
AUTH       = HTTPBasicAuth("admin", "")   # adjust if you set a password

def run_xquery(xquery: str):
    """
    Send an XQuery to eXist-DB via REST and return the parsed XML tree.
    """
    resp = requests.get(
        EXIST_REST,
        params={"_query": xquery, "_howmany": "-1"},
        auth=AUTH,
        headers={"Accept": "application/xml"}
    )
    resp.raise_for_status()
    return etree.fromstring(resp.content)

if __name__ == "__main__":
    # 1. Missions whose Objective mentions “life”
    q1 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      where contains(lower-case($m/metadata_table/metadata[key='Objective']/value), 'life')
      return
        <mission>
          <title>{data($m/title)}</title>
          <objective>{data($m/metadata_table/metadata[key='Objective']/value)}</objective>
        </mission>
    '''

    # 2. Missions launched between two dates
    q2 = '''xquery version "3.1";
      let $start := xs:dateTime('2003-01-01T00:00:00')
      let $end   := xs:dateTime('2013-12-31T23:59:59')
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      let $d := xs:dateTime($m/date)
      where $d >= $start and $d <= $end
      order by $d
      return
        <mission>
          <title>{data($m/title)}</title>
          <date>{data($m/date)}</date>
        </mission>
    '''

    # 3. Upcoming/planned missions
    q3 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      let $d := xs:dateTime($m/date)
      where $d gt current-dateTime()
      order by $d
      return
        <upcoming>
          <title>{data($m/title)}</title>
          <date>{data($m/date)}</date>
        </upcoming>
    '''

    # 4. Missions missing a Subtitle
    q4 = '''xquery version "3.1";
      doc("/db/martian-explorer/missions.xml")/missions/mission
        [not(normalize-space(subtitle))]
        /title
    '''

    # 5. Count of missions by Type
    q5 = '''xquery version "3.1";
      let $types := doc("/db/martian-explorer/missions.xml")/missions/mission/metadata_table/metadata[key='Type']/value
      return
        <counts>{
          for $t in distinct-values($types)
          return <type name="{$t}">{count($types[. = $t])}</type>
        }</counts>
    '''

    # 6. Each mission with its Launch/Landing
    q6 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      let $md := $m/metadata_table/metadata[key='Launch / Landing']/value
      return
        <mission>
          <title>{data($m/title)}</title>
          <launchLanding>{data($md)}</launchLanding>
        </mission>
    '''

    # 7. All story URLs by mission
    q7 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      return
        <mission title="{data($m/title)}">{
          for $s in $m/stories/story
          return <story-url>{data($s/url)}</story-url>
        }</mission>
    '''

    # 8. Free-text search in paragraphs for “atmosphere”
    q8 = '''xquery version "3.1";
      for $p in doc("/db/martian-explorer/missions.xml")//paragraph
      where contains(lower-case($p), 'atmosphere')
      return
        <match mission="{data($p/ancestor::mission/title)}">
          <excerpt>{substring-before($p, '.')}…</excerpt>
        </match>
    '''

    # 9. Distinct partners
    q9 = '''xquery version "3.1";
      distinct-values(
        doc("/db/martian-explorer/missions.xml")
          /missions/mission
          /metadata_table/metadata[key='partner']/value/text()
      )
    '''

    # 10. Missions with “rover” in subtitle
    q10 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      where contains(lower-case($m/subtitle), 'rover')
      return
        <mission>
          <title>{data($m/title)}</title>
          <subtitle>{data($m/subtitle)}</subtitle>
        </mission>
    '''

    # 11. Missions ordered by date descending
    q11 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      let $d := xs:dateTime($m/date)
      order by $d descending
      return
        <mission>
          <title>{data($m/title)}</title>
          <date>{data($m/date)}</date>
        </mission>
    '''

    # 12. Count of news stories per mission
    q12 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      let $count := count($m/stories/story)
      return
        <mission name="{data($m/title)}">
          <storyCount>{$count}</storyCount>
        </mission>
    '''
    
    q13  = '''xquery version "3.1";
        for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
        let $d := xs:date(
            substring-before(
              string($m/date),
              "T"
            )
          )
        where $d = xs:date("2023-06-15")
        return 
          <mission name="{data($m/title)}">
            <date>{$d}</date>
          </mission>
    '''
    
    q14='''
        xquery version "3.1";

        declare variable $from as xs:date := xs:date("2017-06-01");
        declare variable $to   as xs:date := xs:date("2025-06-30");

        for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
        let $pub := xs:date(
                      substring-before(
                        string($m/date),
                        "T"
                      )
                    )
        where $pub >= $from
          and $pub <= $to
        return
          <mission name="{data($m/title)}">
            <date>{$pub}</date>
          </mission>
  '''

    # Store queries in a dict for easy iteration
    queries = {
        'life_objective': q1,
        'date_range': q2,
        'upcoming': q3,
        'missing_subtitle': q4,
        'count_by_type': q5,
        'launch_landing': q6,
        'stories_urls': q7,
        'atmosphere_search': q8,
        'distinct_partners': q9,
        'subtitle_rover': q10,
        'recent_first': q11,
        'story_counts': q12,
        'article_published': q13,
        'article_range_date': q14
    }

    # Execute and print each result
    for name, query in queries.items():
        print(f"--- {name} ---")
        result = run_xquery(query)
        print(etree.tostring(result, pretty_print=True, encoding='unicode'))
