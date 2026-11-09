# Nimbus Campus Helpdesk Agent Toolchain

AI Tools and Prompt Engineering Individual Assignment  
**Student:** Nishi Chopda | **ID:** 150096725128 | **Program:** B.Tech CSE   
**Environment:** Google Antigravity (macOS Darwin arm64)

---

## Repository Structure

```text
.
├── ASSIGNMENT_FINAL_REPORT.md       # Comprehensive audit, test logs, and evidence
├── Nimbus_Labs.docx                 # Full submission report document (Word)
├── Nimbus_Labs.pdf                  # Complete compiled assignment submission report (PDF)
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
│   │           └── timetable_helper.py
│   ├── plugin/
│   │   └── campus-helpdesk/         # Part C: Packaged Antigravity plugin
│   │       ├── plugin.json          # Plugin manifest (official schema v1)
│   │       ├── mcp_config.json      # Stdio MCP configuration with portable python3
│   │       ├── hooks.json           # Documented PreToolUse security hook mapping
│   │       ├── assets/
│   │       │   └── logo.svg         # Bundled 1:1 square plugin logo
│   │       ├── hooks/
│   │       │   └── security_hook.py # Path & command security validator (exit code 0)
│   │       ├── skills/              # Bundled skills
│   │       │   ├── timetable-helper/# Natural language timetable querying
│   │       │   └── timetable/       # /timetable slash command
│   │       └── tests/
│   │           └── test_security_hook.py # Realistic PreToolUse test suite
│   └── mcp-server/                  # Part D: Local stdio MCP server (Python SDK)
│       ├── README.md                # Server run & test documentation
│       ├── requirements.txt         # Server dependencies (mcp>=2.3.0)
│       ├── server.py                # Official MCP Python SDK stdio implementation
│       └── resources/
│           └── hostel-rules.md      # campus://hostel/rules resource
└── evidence/
    ├── mcp/
    │   └── protocol_exchange.log    # Raw JSON-RPC stdio protocol exchange
    ├── plugin/
    │   └── security_hook_test.log   # Hook tests and agy plugin validate output
    ├── skill/
    │   └── skill_tests.log          # Seven separate positive/negative/adversarial tests
    └── worktrees/
        └── worktree_and_conflict.log# Git worktree list, conflict, and graph
```

---

## Quick Start & Verification

### 1. Test the Agent Skill Script (Part B)
```bash
python3 campus-helpdesk/skills/timetable-helper/scripts/timetable_helper.py --batch CS-A --day Monday
```

### 2. Run the Security Hook Tests & Validate Plugin (Part C)
```bash
# Run security hook test suite (7 realistic test cases, all exit code 0)
python3 campus-helpdesk/plugin/campus-helpdesk/tests/test_security_hook.py

# Run strict Antigravity plugin validation
agy plugin validate --strict campus-helpdesk/plugin/campus-helpdesk
```

### 3. Launch and Test the MCP Server (Part D)
```bash
# Start standalone stdio server
python3 campus-helpdesk/mcp-server/server.py
```
Or run the full automated stdio protocol handshake:
```bash
python3 -c '
import subprocess, json
proc = subprocess.Popen(["python3", "campus-helpdesk/mcp-server/server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
def send(req):
    proc.stdin.write(json.dumps(req) + "\n"); proc.stdin.flush()
    return json.loads(proc.stdout.readline())

print("1. Initialize:", send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}))
proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"); proc.stdin.flush()
print("2. Tools List:", send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
print("3. Timetable Tool:", send({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_timetable", "arguments": {"batch": "CS-A", "day": "Monday"}}}))
print("4. Hostel Resource:", send({"jsonrpc": "2.0", "id": 4, "method": "resources/read", "params": {"uri": "campus://hostel/rules"}}))
proc.terminate()
'
```

### 4. Git Worktrees (Part E)
```bash
git worktree list
```
All evidence files are maintained under `evidence/`.
