# The Martian Explorer

*Chaos to Cosmos*

Explore Mars missions with advanced filtering, summarization, and a web UI backed by eXist-DB.

---

## 📑 Web UI Screenshot

<img width="1376" height="828" alt="Screenshot 2025-07-24 at 17 15 22" src="https://github.com/user-attachments/assets/cc68a245-b00a-463e-a784-73c5465264fd" />


*Explore missions, filter by type/status/date, and drill into news stories.*

---

## 🚀 Project Overview

The Martian Explorer is a three-stage data-pipeline + web-app:

1. **Collect**
   Scrapes NASA’s Science site for Mars mission pages, extracts mission metadata & stories into JSON.

2. **Prepare**
   Transforms JSON into a single validated XML file (`missions.xml`), then uploads it into an eXist-DB collection.

3. **Access**
   Serves a React/Vite app that queries eXist-DB via XQuery REST, building an interactive mission browser.

**All three steps (plus starting eXist-DB and your UI) can be run automatically with a single script!**

---

## 🗂 Repo Layout

```
/ themartianexplorer
├─ 1.Collect/
│   └─ scrapper.py              # MarsMissionScraper → raw JSON in raw_missions/
│   └─ raw_missions             # JSON format for raw scrapped data
├─ 2.Prepare/
│   ├─ json_to_xml.py           # JSON → missions.xml (+ XSD validation)
│   ├─ missions.xml             # Generated XML
│   ├─ mission.xsd              # XML Grammar - XML Schema Definition - XSD
│   └─ upload_missions.py       # PUT missions.xml into eXist-DB
├─ 3.Access/
│   └─ user-interface/          # React/Vite app
│     └─ utils/                
│        └─ xquery-builder.tsx  # utility to build xquery based on user interaction 
├─ venv/                        # Python virtualenv
├─ .env                         # Environment variables (GROQ_API_KEY)
├─ requirements.txt             # All python packages required to run the project
├─ run_pipeline.sh              # Bash wrapper to bootstrap DB, run all scripts & npm dev
└─ README.md
```

---

## Access Flow
React UI Components -> Custom Hooks and Utilities -> API Routes & eXist-DB

## User Interaction Flow
User Input → Filter State → XQuery → eXist-DB → XML → Parsed Data → UI Update

---

## ⚙️ Prerequisites

* **Docker** (to run eXist-DB)
* **Python 3.8+**
* **Node.js 16+ & npm**

---

## 🛠️ Setup

1. **Clone & enter repo**

   ```bash
   git clone https://github.com/Anniebhalla16/themartianexplorer.git
   cd themartianexplorer
   ```

2. **Create & activate Python venv**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create your .env**
   At the project root, create a file named `.env` and add your GROQ API key:

   ```bash
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

   This key is used by the data-collection script to summarize mission overviews via Groq.
   Hint: Create your free groq api key using this quick tutorial https://youtu.be/TTG7Uo8lS1M?si=-DxERoc_4ZkPEmP6

5. **Install UI deps**

   ```bash
   cd 3.Access/user-interface
   npm install
   cd ../../
   ```

---

## 🔄 Using the Pipeline Script

Once you’ve set up your environment and `.env` file, you can run **everything** with one command:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

This will:

1. Stop & remove any existing `existdb` container
2. Start eXist-DB on `localhost:8080`
3. Run `scrapper.py` → JSON files
4. Run `json_to_xml.py` → `missions.xml`
5. Run `upload_missions.py` → load into eXist-DB
6. Launch the React dev server (`npm run dev`) on `localhost:3000`

If you prefer, you can run each step manually:

```bash
# 1) Start DB
docker run -d --name existdb -p 8080:8080 existdb/existdb:latest

# 2) Collect data
source venv/bin/activate
python3 1.Collect/scrapper.py

# 3) Prepare XML
python3 2.Prepare/json_to_xml.py

# 4) Upload to DB
python3 2.Prepare/upload_missions.py

# 5) Launch UI
cd 3.Access/user-interface
npm run dev
```


---

Enjoy exploring the Red Planet!
— Annie & MarsMissionScraper 🤖🚀
