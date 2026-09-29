#!/usr/bin/env bash
# Download (first run only) and start a local LanguageTool server on port 8081.
# Requires Java 17+ and Maven. Then set LANGUAGETOOL_URL=http://localhost:8081/v2/check
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d libs ]; then
  mvn -q dependency:copy-dependencies -DoutputDirectory=libs
fi
exec java -cp "libs/*" org.languagetool.server.HTTPServer --port "${PORT:-8081}" --allow-origin
