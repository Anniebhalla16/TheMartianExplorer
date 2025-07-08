import json
import os
from lxml import etree

JSON_DIR = "/Users/anniebhalla/Desktop/Universität Stuttgart/Projects/TheMartianExplorer/1.Collect/raw_missions/"
XML_OUTPUT = "/Users/anniebhalla/Desktop/Universität Stuttgart/Projects/TheMartianExplorer/2.Prepare/missions.xml"
XSD_PATH = "/Users/anniebhalla/Desktop/Universität Stuttgart/Projects/TheMartianExplorer/2.Prepare/mission.xsd"

# Read all JSON files from directory
data = []
for filename in os.listdir(JSON_DIR):
    if filename.endswith('.json'):
        filepath = os.path.join(JSON_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            mission_data = json.load(f)
            data.append(mission_data)

print(f"📁 Loaded {len(data)} JSON files from '{JSON_DIR}'")

# --- BUILD XML TREE ---
missions_el = etree.Element("missions")

for entry in data:
    mission_el = etree.SubElement(missions_el, "mission")
    
    # Add simple fields (can be empty)
    for field in ["title", "subtitle", "url", "date", "stories_page_url", "scraped_at"]:
        value = entry.get(field, "")
        etree.SubElement(mission_el, field).text = str(value) if value else ""
    
    # Add paragraphs (can be empty array)
    paragraphs_el = etree.SubElement(mission_el, "paragraphs")
    if "paragraphs" in entry and entry["paragraphs"]:
        for paragraph in entry["paragraphs"]:
            etree.SubElement(paragraphs_el, "paragraph").text = paragraph or ""
    
    # Add metadata table (can be empty array)
    metadata_table_el = etree.SubElement(mission_el, "metadata_table")
    if "metadata_table" in entry and entry["metadata_table"]:
        for metadata in entry["metadata_table"]:
            metadata_el = etree.SubElement(metadata_table_el, "metadata")
            etree.SubElement(metadata_el, "key").text = metadata.get("key", "")
            etree.SubElement(metadata_el, "value").text = metadata.get("value", "")
    
    # Add stories (can be empty array)
    stories_el = etree.SubElement(mission_el, "stories")
    if "stories" in entry and entry["stories"]:
        for story in entry["stories"]:
            story_el = etree.SubElement(stories_el, "story")
            etree.SubElement(story_el, "title").text = story.get("title", "")
            etree.SubElement(story_el, "url").text = story.get("url", "")
            etree.SubElement(story_el, "type").text = story.get("type", "")
            etree.SubElement(story_el, "story_image_url").text = story.get("story_image_url", "")
            
            
    status = entry.get("mission_status", "")
    status_el = etree.SubElement(mission_el, "missions_status")
    status_el.text = status or ""

xml_tree = etree.ElementTree(missions_el)

# --- VALIDATE WITH XSD ---
with open(XSD_PATH, "rb") as xsd_file:
    schema_doc = etree.parse(xsd_file)
    schema = etree.XMLSchema(schema_doc)

if schema.validate(xml_tree):
    # Save only if valid
    xml_tree.write(XML_OUTPUT, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"✅ XML saved as '{XML_OUTPUT}' and validated successfully against '{XSD_PATH}'")
else:
    print("❌ XML did not validate:")
    for error in schema.error_log:
        print(" -", error.message)