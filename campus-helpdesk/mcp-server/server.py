#!/usr/bin/env python3
"""
server.py
Campus Helpdesk MCP Server implementing Model Context Protocol (JSON-RPC 2.0 stdio).
Provides:
  - Tools: get_timetable, get_fee_status
  - Resources: hostel-rules (URI: campus://hostel/rules)
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, Any, List

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "campus-helpdesk-mcp"
SERVER_VERSION = "1.0.0"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TIMETABLE_CSV = DATA_DIR / "timetable.csv"
FEES_JSON = DATA_DIR / "mock_fees.json"
HOSTEL_RULES_MD = Path(__file__).resolve().parent / "resources" / "hostel-rules.md"


def send_response(response: Dict[str, Any]):
    msg = json.dumps(response)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def load_timetable() -> List[Dict[str, str]]:
    if not TIMETABLE_CSV.exists():
        return []
    with open(TIMETABLE_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k.strip(): v.strip() for k, v in row.items()} for row in reader]


def load_fees() -> Dict[str, Any]:
    if not FEES_JSON.exists():
        return {}
    with open(FEES_JSON, mode="r", encoding="utf-8") as f:
        return json.load(f)


def handle_initialize(req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {
                "tools": {
                    "listChanged": False
                },
                "resources": {
                    "subscribe": False,
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION
            }
        }
    }


def handle_tools_list(req_id: Any) -> Dict[str, Any]:
    tools = [
        {
            "name": "get_timetable",
            "description": "Retrieve class schedule and room details for a given academic batch and day from mock timetable data. Returns matching rows in chronological order.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "batch": {
                        "type": "string",
                        "description": "Student academic batch (e.g., 'CS-A', 'CS-B')"
                    },
                    "day": {
                        "type": "string",
                        "description": "Day of the week (e.g., 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')"
                    }
                },
                "required": ["batch", "day"]
            }
        },
        {
            "name": "get_fee_status",
            "description": "Retrieve financial fee status, paid amount, pending balance, and payment status for a fictional student ID. Does not access or expose real student records.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Fictional student identifier (e.g., '2024CS001', '2024CS002', '2024CS015')"
                    }
                },
                "required": ["student_id"]
            }
        }
    ]
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "tools": tools
        }
    }


def handle_tools_call(req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    args = params.get("arguments", {})

    if name == "get_timetable":
        batch = args.get("batch", "").strip()
        day = args.get("day", "").strip()

        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        matched_day = next((d for d in valid_days if d.lower() == day.lower()), None)
        if not matched_day:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Validation Error: Invalid day '{day}'. Valid days are Monday through Friday."
                        }
                    ],
                    "isError": True
                }
            }

        records = load_timetable()
        filtered = [
            r for r in records
            if r.get("batch", "").lower() == batch.lower() and r.get("day", "").lower() == matched_day.lower()
        ]
        filtered.sort(key=lambda x: x.get("start_time", "00:00"))

        if not filtered:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"No timetable records found for batch '{batch}' on {matched_day}."
                        }
                    ]
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(filtered, indent=2)
                    }
                ]
            }
        }

    elif name == "get_fee_status":
        student_id = args.get("student_id", "").strip()
        fees = load_fees()
        record = fees.get(student_id)

        if not record:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Student record not found for ID '{student_id}'. Fictional fee information cannot be fabricated."
                        }
                    ],
                    "isError": True
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(record, indent=2)
                    }
                ]
            }
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Tool not found: {name}"
            }
        }


def handle_resources_list(req_id: Any) -> Dict[str, Any]:
    resources = [
        {
            "uri": "campus://hostel/rules",
            "name": "Hostel Rules & Regulations",
            "description": "Official campus hostel rules including gate curfew, visitor policy, and conduct regulations.",
            "mimeType": "text/markdown"
        }
    ]
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "resources": resources
        }
    }


def handle_resources_read(req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    uri = params.get("uri")
    if uri == "campus://hostel/rules":
        if HOSTEL_RULES_MD.exists():
            text = HOSTEL_RULES_MD.read_text(encoding="utf-8")
        else:
            text = "Hostel rules document not found."
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": text
                    }
                ]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32602,
                "message": f"Resource URI not found: {uri}"
            }
        }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            })
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            send_response(handle_initialize(req_id, params))
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            send_response(handle_tools_list(req_id))
        elif method == "tools/call":
            send_response(handle_tools_call(req_id, params))
        elif method == "resources/list":
            send_response(handle_resources_list(req_id))
        elif method == "resources/read":
            send_response(handle_resources_read(req_id, params))
        elif method == "ping":
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {}})
        else:
            if req_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                })


if __name__ == "__main__":
    main()

