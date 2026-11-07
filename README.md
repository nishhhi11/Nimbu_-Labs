# Nimbus Campus Helpdesk Agent Toolchain

AI Tools and Prompt Engineering Individual Assignment  
**Student:** Nishi Chopda | **ID:** 150096725128 | **Program:** B.Tech CSE   
**Environment:** Google Antigravity (macOS Darwin arm64)

---

## Repository Structure

```text
.
├── ASSIGNMENT_FINAL_REPORT.md       # Comprehensive audit, test logs, and evidence
├── Nimbus_Campus_Helpdesk_Assignment_Nishi_Chopda.docx  # Full submission report
├── data/
│   ├── mock_fees.json               # Fictional student fee records
│   └── timetable.csv                # Complete mock timetable dataset
├── campus-helpdesk/
│   ├── skills/
│   │   └── timetable-helper/        # Part B: Agent Skill with progressive disclosure
│   │       ├── SKILL.md
│   │       ├── references/
│   │       │   ├── csv-column-dictionary.md
│   │       │   ├── edge-cases.md
│   │       │   ├── lookup-guide.md
│   │       │   └── mock_timetable.csv
│   │       └── scripts/
│   │           ├── timetable_helper.py
│   │           └── timetable_lookup.py
│   ├── plugin/
│   │   └── campus-helpdesk/         # Part C: Packaged plugin
│   │       ├── plugin.json          # Plugin manifest
│   │       ├── mcp_config.json      # Stdio MCP configuration
│   │       ├── hooks.json           # PreToolUse security hook mapping
│   │       ├── commands/
│   │       │   └── timetable.md     # /timetable slash command
│   │       ├── hooks/
│   │       │   └── security_hook.py # Path and command security validator
│   │       └── skills/              # Bundled skill
│   └── mcp-server/                  # Part D: Local stdio MCP server
│       ├── README.md                # Server run & test documentation
│       ├── server.py                # JSON-RPC 2.0 stdio server implementation
│       └── resources/
│           └── hostel-rules.md      # campus://hostel/rules resource
```

---

## Quick Start & Verification

### 1. Test the Agent Skill Script
```bash
python3 campus-helpdesk/skills/timetable-helper/scripts/timetable_helper.py --batch CS-A --day Monday
```

### 2. Test the Security Hook
```bash
# Safe operation (allowed, exit code 0)
python3 campus-helpdesk/plugin/campus-helpdesk/hooks/security_hook.py "ls -la"

# Dangerous path traversal (blocked, exit code 1)
python3 campus-helpdesk/plugin/campus-helpdesk/hooks/security_hook.py "cat /etc/passwd"
```

### 3. Launch and Test the MCP Server
```bash
python3 campus-helpdesk/mcp-server/server.py
```
Or test protocol negotiation and tool invocation:
```bash
python3 -c '
import subprocess, json
proc = subprocess.Popen(["python3", "campus-helpdesk/mcp-server/server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}}
proc.stdin.write(json.dumps(req) + "\n"); proc.stdin.flush()
print("Initialize Handshake:", proc.stdout.readline().strip())
proc.terminate()
'
```

