import requests
from requests.auth import HTTPBasicAuth
from lxml import etree

EXIST_REST = "http://localhost:8080/exist/rest/db/martian-explorer/missions.xml"
AUTH       = HTTPBasicAuth("admin", "")   # adjust if you set a password

def run_xquery(xquery: str):
    """
    Send an XQuery to eXist-DB via REST and return the parsed XML tree.
    """
    resp = requests.get(
        EXIST_REST,
        params={"_query": xquery, "_howmany":"-1"},
        auth=AUTH,
        headers={"Accept": "application/xml"}
    )
    resp.raise_for_status()
    return etree.fromstring(resp.content)

if __name__ == "__main__":
    # Example 1: list all mission names
    q1 = '''xquery version "3.1";
      for $m in doc("/db/martian-explorer/missions.xml")/missions/mission
      return <title>{ data($m/title) }</title>
    '''
    
    root1 = run_xquery(q1)
    titles = [e.text for e in root1.findall(".//title")]
    print("Mission names:", titles)

    # Example 2: list all unique mission types
    q2 = '''xquery version "3.1";
       distinct-values(
         doc("/db/martian-explorer/missions.xml")
           /missions/mission
           /metadata_table/metadata
             [key = 'Type']
             /value/text()
       )
     '''
    root2 = run_xquery(q2)
    # collect all distinct-values() results from the returned XML
    types = [t.strip() for t in root2.xpath("//*[local-name()='string']|//text()") if t.strip()]
    print("Mission types:", types)

    q3 = '''xquery version "3.1";
       distinct-values(
         doc("/db/martian-explorer/missions.xml")
           /missions/mission
           /metadata_table/metadata
             [key = 'Target']
             /value/text()
       )
     '''
     
    root3 = run_xquery(q3)
    targets = [t.strip() for t in root3.xpath("//*[local-name()='string']|//text()") if t.strip()]
    print("Mission targets:", targets)