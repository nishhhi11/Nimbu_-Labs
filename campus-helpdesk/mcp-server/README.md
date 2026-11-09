# Campus Helpdesk MCP Server

Official Model Context Protocol (MCP) server for university student services implemented with the **Official MCP Python SDK** (`mcp>=2.3.0`) over standard input/output (`stdio`).

## Primitives Exposed

### 1. Tools
- **`get_timetable(batch, day)`**
  - **Inputs:** `batch` (e.g. `CS-A`, `CS-B`), `day` (e.g. `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`)
  - **Output:** Chronologically sorted list of scheduled classes with start/end time, subject code, subject title, faculty name, and room/lab location.
  - **Error Handling:** Validates string inputs and weekdays; returns descriptive error messages for invalid days or missing batch records without fabricating data.
- **`get_fee_status(student_id)`**
  - **Inputs:** `student_id` (e.g. `2024CS001`, `2024CS002`, `2024CS015`)
  - **Output:** Financial fee profile including student name, total fees, paid amount, pending balance, and payment status.
  - **Security Guarantee:** Operates strictly on mock student records (`data/mock_fees.json`). Nonexistent student IDs return explicit not-found errors and are never fabricated.

### 2. Resources
- **Hostel Rules Document**
  - **URI:** `campus://hostel/rules`
  - **MIME Type:** `text/markdown`
  - **Content:** Campus hostel regulations covering main gate curfews (22:00 weekdays / 23:00 weekends), visiting hours, electrical appliance restrictions, and code of conduct.

---

## Package Verification Note (`@nimbus/mcp-skill-bridge`)
The CTO briefing suggested using `@nimbus/mcp-skill-bridge` (v2.3) to auto-convert Skills into MCP tools.
- **Verification Result:** Lookups against npm and PyPI returned `404 Not Found`.
- **Decision:** Rejected as a fictional package. The server is built directly using the official `mcp` Python SDK (`from mcp.server.mcpserver import MCPServer`).

---

## Run and Test Instructions

### Running Standalone
```bash
python3 server.py
```
The server reads JSON-RPC 2.0 requests from `stdin` and writes JSON-RPC 2.0 responses to `stdout`.

### Testing via MCP Inspector
```bash
npx @modelcontextprotocol/inspector python3 server.py
```

### Direct JSON-RPC Stdio Testing
```bash
python3 -c '
import subprocess, json

proc = subprocess.Popen(["python3", "server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def send(method, params=None, req_id=1):
    req = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params: req["params"] = params
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())

print("Initialize:", send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}))
proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
proc.stdin.flush()
print("Tools List:", send("tools/list", req_id=2))
print("Tool Call (get_timetable):", send("tools/call", {"name": "get_timetable", "arguments": {"batch": "CS-A", "day": "Monday"}}, req_id=3))
print("Tool Call (get_fee_status):", send("tools/call", {"name": "get_fee_status", "arguments": {"student_id": "2024CS001"}}, req_id=4))
print("Resource Read:", send("resources/read", {"uri": "campus://hostel/rules"}, req_id=5))
proc.terminate()
'
```
