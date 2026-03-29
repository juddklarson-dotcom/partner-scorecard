#!/bin/bash
# ──────────────────────────────────────────────────────────
# Partner Scorecard — Mac Launcher
# Double-click this file to start the app.
# ──────────────────────────────────────────────────────────

cd "$(dirname "$0")"

echo ""
echo "  Partner Scorecard"
echo "  ─────────────────"
echo ""

# ── Check for Python 3 ──
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PY=python
else
    echo "  Python 3 is required but not installed."
    echo ""
    echo "  Install it from: https://www.python.org/downloads/"
    echo ""
    echo "  Press any key to close..."
    read -n 1
    exit 1
fi

echo "  Using $($PY --version)"

# ── Create virtual environment if needed ──
if [ ! -d ".venv" ]; then
    echo "  Setting up (first run only)..."
    $PY -m venv .venv
fi

# ── Activate and install dependencies ──
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

echo "  Starting app — your browser will open shortly..."
echo ""

# ── Launch ──
streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
