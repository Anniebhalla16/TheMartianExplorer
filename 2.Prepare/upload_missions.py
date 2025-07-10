#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth

# 1) Configuration
EXIST_URL    = "http://localhost:8080/exist/webdav/db"
COLLECTION   = "martian-explorer"
XML_FILE     = "missions.xml"
USERNAME     = "admin"
PASSWORD     = ""  

auth = HTTPBasicAuth(USERNAME, PASSWORD)

# 2) Create the collection via MKCOL
collector_url = f"{EXIST_URL}/{COLLECTION}"
resp = requests.request("MKCOL", collector_url, auth=auth)
if resp.status_code in (201, 405):
    # Status Code - 201 Created successfully
    print(f"Collection '{COLLECTION}' ready (HTTP {resp.status_code}).")
else:
    print(f"Failed to create collection: HTTP {resp.status_code}\n{resp.text}")
    exit(1)

# 3) Upload the XML via PUT
with open(XML_FILE, "rb") as f:
    xml_bytes = f.read()

upload_url = f"{collector_url}/{XML_FILE}"
headers = {"Content-Type": "application/xml; charset=UTF-8"}
resp = requests.put(upload_url, data=xml_bytes, auth=auth, headers=headers)

if resp.status_code in (200, 201, 204):
    print(f"Uploaded '{XML_FILE}' to '/db/{COLLECTION}'.")
else:
    print(f"Failed to upload file: HTTP {resp.status_code}\n{resp.text}")
    exit(1)
