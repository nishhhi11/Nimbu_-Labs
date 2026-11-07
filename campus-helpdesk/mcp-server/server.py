"""
server.py
Compliant MCP Server for Nimbus Campus Helpdesk using the Official Python MCP SDK (v2).
Exposes:
  - Tools: get_timetable(batch, day), get_fee_status(student_id)
  - Resources: campus://hostel/rules (hostel-rules.md)
Transport: stdio
"""

import sys
from pathlib import Path

# Add project venv site-packages to sys.path so IDE linters and runtime find the MCP SDK
VENV_PACKAGES = Path(__file__).resolve().parent / ".venv" / "lib" / "python3.14" / "site-packages"
if VENV_PACKAGES.exists() and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

import csv
import json
from typing import List, Dict, Any

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    # Fallback to local import if run with external Python
    from mcp.server.mcpserver import MCPServer

# Initialize MCPServer (Official MCP Python SDK v2)
mcp = MCPServer("campus-helpdesk-mcp")

# Path resolutions
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TIMETABLE_CSV = DATA_DIR / "timetable.csv"
FEES_JSON = DATA_DIR / "mock_fees.json"
HOSTEL_RULES_MD = Path(__file__).resolve().parent / "resources" / "hostel-rules.md"

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def load_timetable_data() -> List[Dict[str, str]]:
    if not TIMETABLE_CSV.exists():
        return []
    with open(TIMETABLE_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k.strip(): v.strip() for k, v in row.items()} for row in reader]


def load_fees_data() -> Dict[str, Any]:
    if not FEES_JSON.exists():
        return {}
    with open(FEES_JSON, mode="r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def get_timetable(batch: str, day: str) -> str:
    """
    Retrieve scheduled classes, lecture timings, rooms, and faculty for an academic batch and day.

    Args:
        batch: Academic cohort identifier (e.g. 'CS-A', 'CS-B')
        day: Day of the week (e.g. 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')
    """
    if not isinstance(batch, str) or not isinstance(day, str):
        return "Validation Error: 'batch' and 'day' arguments must be strings."

    batch_clean = batch.strip()
    day_clean = day.strip()

    matched_day = next((d for d in VALID_DAYS if d.lower() == day_clean.lower()), None)
    if not matched_day:
        return f"Validation Error: Invalid day '{day_clean}'. Classes run Monday through Friday."

    records = load_timetable_data()
    filtered = [
        r for r in records
        if r.get("batch", "").lower() == batch_clean.lower() and r.get("day", "").lower() == matched_day.lower()
    ]

    filtered.sort(key=lambda x: x.get("start_time", "00:00"))

    if not filtered:
        return f"No timetable records found for batch '{batch_clean}' on {matched_day}."

    return json.dumps(filtered, indent=2)


@mcp.tool()
def get_fee_status(student_id: str) -> str:
    """
    Retrieve financial payment record, tuition fees, paid amount, and pending balance for a fictional student ID.

    Args:
        student_id: Fictional student identifier (e.g. '2024CS001', '2024CS002', '2024CS015')
    """
    if not isinstance(student_id, str):
        return "Validation Error: 'student_id' must be a string."

    sid_clean = student_id.strip()
    fees_db = load_fees_data()

    if sid_clean not in fees_db:
        return f"Error: Student record '{sid_clean}' not found. Fictional fee information cannot be fabricated."

    return json.dumps(fees_db[sid_clean], indent=2)


@mcp.resource("campus://hostel/rules")
def get_hostel_rules() -> str:
    """Official campus hostel rules, curfew timings, and visitor policies."""
    if HOSTEL_RULES_MD.exists():
        return HOSTEL_RULES_MD.read_text(encoding="utf-8")
    return "Hostel rules document not found on server."


if __name__ == "__main__":
    mcp.run(transport="stdio")
