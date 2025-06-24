import json
from lxml import etree

JSON_PATH = "/Users/anniebhalla/Desktop/Universität Stuttgart/Projects/TheMartianExplorer/collect/missions.json"
XML_OUTPUT = "/Users/anniebhalla/Desktop/Universität Stuttgart/Projects/TheMartianExplorer/prepare/missions.xml"
XSD_PATH = "/Users/anniebhalla/Desktop/Universität Stuttgart/Projects/TheMartianExplorer/prepare/mission.xsd"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# --- BUILD XML TREE ---
missions_el = etree.Element("missions")

for entry in data:
    mission_el = etree.SubElement(missions_el, "mission")
    
    def add(tag):
        if tag in entry:
            etree.SubElement(mission_el, tag).text = entry[tag]
    
    # Required and optional fields
    for field in ["mission_name", "type", "launch", "target", "objective", "wavelength", "graphic", "weblink"]:
        add(field)

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
