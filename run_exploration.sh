#!/usr/bin/env bash
set -euo pipefail

# ─── 0) Activate your virtualenv ─────────────────────────────────────────────
VENV_DIR="./venv"
if [[ -f "${VENV_DIR}/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
  echo "✔ Activated virtualenv at ${VENV_DIR}"
else
  echo "Error: Virtualenv not found at ${VENV_DIR}. Have you run 'python3 -m venv venv'?" >&2
  exit 1
fi

# ─── 1) Ensure Python 3 is available ──────────────────────────────────────────
PYTHON=${PYTHON:-python3}
if ! command -v "${PYTHON}" &> /dev/null; then
  echo "Error: ${PYTHON} not found. Please install Python 3 or adjust the PYTHON variable." >&2
  exit 1
fi

# ─── Configuration ────────────────────────────────────────────────────────────
COLLECT_SCRIPT="./1.Collect/scrapper.py"
PREPARE_SCRIPT="./2.Prepare/json_to_xml.py"
UPLOAD_SCRIPT="./2.Prepare/upload_missions.py"
UI_DIR="./3.Access/user-interface"

DB_CONTAINER_NAME="existdb"
DB_IMAGE="existdb/existdb:latest"
DB_PORT="8080:8080"

function log() {
  echo "[$(date +'%H:%M:%S')] $*"
}

# ─── 2) Restart eXist-DB ───────────────────────────────────────────────────────
docker stop "${DB_CONTAINER_NAME}" 2>/dev/null || true
docker rm   "${DB_CONTAINER_NAME}" 2>/dev/null || true
docker run -d --name "${DB_CONTAINER_NAME}" -p "${DB_PORT}" "${DB_IMAGE}"

# ─── Wait for eXist to be ready ───────────────────────────────────────────────
echo -n "Waiting for eXist-DB to listen on port 8080…"
until curl -s http://localhost:8080/exist/ > /dev/null; do
  printf "."
  sleep 2
done
echo " OK — eXist-DB is up!"

# ─── 3) Collect data ──────────────────────────────────────────────────────────
log "Running collector script…"
"${PYTHON}" "${COLLECT_SCRIPT}"

# ─── 4) Prepare (JSON → XML) ──────────────────────────────────────────────────
log "Running prepare script (JSON → XML)…"
"${PYTHON}" "${PREPARE_SCRIPT}"

# ─── 5) Upload to DB ─────────────────────────────────────────────────────────
log "Running upload script (PUT to eXist-DB)…"
pushd "$(dirname "${UPLOAD_SCRIPT}")" >/dev/null
"${PYTHON}" "$(basename "${UPLOAD_SCRIPT}")"
popd >/dev/null

# ─── 6) Launch UI ───────────────────────────────────────────────────────
log "Changing directory to UI at '${UI_DIR}' and running npm run dev…"
cd "${UI_DIR}"
npm run dev
