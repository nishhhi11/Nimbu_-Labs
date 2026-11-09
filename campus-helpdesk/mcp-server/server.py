"""
server.py
Compliant MCP Server for Nimbus Campus Helpdesk using the Official Python MCP SDK.
Exposes:
  - Tools: get_timetable(batch, day), get_fee_status(student_id)
  - Resources: campus://hostel/rules (hostel-rules.md)
Transport: stdio
"""

import os
import sys
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.mcpserver import MCPServer

# Initialize MCPServer using the Official MCP Python SDK
mcp = MCPServer(
    name="campus-helpdesk-mcp",
    version="1.0.0",
    description="Campus Helpdesk MCP Server for timetables, fees, and hostel rules",
)

def _resolve_data_dir() -> Path:
    """
    Resolve data directory portably:
    1. PLUGIN_ROOT environment variable (when launched as Antigravity plugin)
    2. Parent directory's data/ (e.g. plugin root: campus-helpdesk/plugin/campus-helpdesk/data/)
    3. Grandparent directory's data/ (e.g. source repo root: campus-helpdesk/data/)
    """
    if "PLUGIN_ROOT" in os.environ:
        plugin_data = Path(os.environ["PLUGIN_ROOT"]) / "data"
        if plugin_data.exists():
            return plugin_data

    server_dir = Path(__file__).resolve().parent

    # Check sibling/parent locations
    candidates = [
        server_dir.parent / "data",              # <plugin-root>/data
        server_dir.parent.parent / "data",       # <repo-root>/data or <repo-root>/campus-helpdesk/data
        server_dir / "data",
    ]
    for c in candidates:
        if c.exists():
            return c

    # Fallback to direct parent
    return server_dir.parent / "data"


def _resolve_resource_path() -> Path:
    """Resolve hostel rules document portably."""
    server_dir = Path(__file__).resolve().parent
    local_rules = server_dir / "resources" / "hostel-rules.md"
    if local_rules.exists():
        return local_rules

    if "PLUGIN_ROOT" in os.environ:
        plugin_rules = Path(os.environ["PLUGIN_ROOT"]) / "mcp-server" / "resources" / "hostel-rules.md"
        if plugin_rules.exists():
            return plugin_rules

    return local_rules


DATA_DIR = _resolve_data_dir()
TIMETABLE_CSV = DATA_DIR / "timetable.csv"
FEES_JSON = DATA_DIR / "mock_fees.json"
HOSTEL_RULES_MD = _resolve_resource_path()

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

    if not batch_clean or not day_clean:
        return "Validation Error: 'batch' and 'day' cannot be empty."

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
    if not sid_clean:
        return "Validation Error: 'student_id' cannot be empty."

    fees_db = load_fees_data()

    if sid_clean not in fees_db:
        return f"Error: Student record '{sid_clean}' not found. Fictional fee information cannot be fabricated."

    return json.dumps(fees_db[sid_clean], indent=2)


@mcp.resource("campus://hostel/rules", mime_type="text/markdown")
def get_hostel_rules() -> str:
    """Official campus hostel rules, curfew timings, and visitor policies."""
    rules_file = _resolve_resource_path()
    if rules_file.exists():
        return rules_file.read_text(encoding="utf-8")
    return "Hostel rules document not found on server."


if __name__ == "__main__":
    mcp.run(transport="stdio")
