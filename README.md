# Nimbus Campus Helpdesk Agent Toolchain

AI Tools and Prompt Engineering Individual Assignment  
**Student:** Nishi Chopda | **Program:** B.Tech CSE   
**Environment:** Google Antigravity (macOS Darwin arm64)

---

## Repository Structure

```text
.
├── ASSIGNMENT_FINAL_REPORT.md       # Comprehensive audit, test logs, and evidence
├── Nimbus_Labs.docx                 # Full submission report document (Word)
├── prompt_log.txt                   # Verified chronological prompt and verification log
├── campus-helpdesk/
│   ├── data/                        # Shared mock datasets
│   │   ├── mock_fees.json           # Fictional student fee records
│   │   └── timetable.csv            # Complete mock timetable dataset
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
│   │       ├── mcp_config.json      # Stdio MCP configuration (/bin/sh exec wrapper)
│   │       ├── hooks.json           # Documented PreToolUse security hook mapping
│   │       ├── README.md            # Plugin setup and testing documentation
│   │       ├── assets/
│   │       │   └── logo.svg         # Bundled 1:1 square plugin logo
│   │       ├── data/                # Plugin-bundled mock datasets
│   │       │   ├── mock_fees.json
│   │       │   └── timetable.csv
│   │       ├── hooks/
│   │       │   └── security_hook.py # Path & command security validator (exit code 0)
│   │       ├── mcp-server/          # Bundled MCP server package and venv
│   │       │   ├── README.md
│   │       │   ├── requirements.txt
│   │       │   ├── server.py
│   │       │   └── resources/
│   │       │       └── hostel-rules.md
│   │       ├── skills/              # Bundled skills
│   │       │   ├── timetable-helper/# Natural language timetable querying
│   │       │   └── timetable/       # /timetable slash command
│   │       └── tests/
│   │           └── test_security_hook.py # Realistic PreToolUse test suite
│   └── mcp-server/                  # Part D: Standalone stdio MCP server package
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
    ├── screenshots/
    │   ├── part_b_skill_tests.png
    │   ├── part_c_plugin_validation.png
    │   ├── part_c_security_hook.png
    │   ├── part_d_mcp_exchange.png
    │   ├── part_d_mcp_inspector.png
    │   └── part_e_worktree_conflict.png
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
# Run security hook test suite (all exit code 0)
python3 campus-helpdesk/plugin/campus-helpdesk/tests/test_security_hook.py

# Run strict Antigravity plugin validation
# If `agy` is on your PATH:
agy plugin validate --strict campus-helpdesk/plugin/campus-helpdesk

# If `agy` is installed locally under ~/.gemini/bin:
/Users/nishi/.gemini/bin/agy plugin validate --strict campus-helpdesk/plugin/campus-helpdesk
```

### 3. Setup, Launch, and Test the MCP Server (Part D)

#### Step 3a: Environment Setup (If initializing a fresh clone)
The MCP server and modern SDK dependencies require a modern Python runtime matching the project's tested environment (**Python 3.14.8**). The default macOS system Python (`python3` v3.9.6) lacks required modern typing features (`typing.TypeAlias`, PEP 604 unions) and cannot import the MCP SDK.

1. **Verify your Python interpreter version:**
   ```bash
   # Check if python3.14 is available:
   python3.14 --version
   ```
   *(Expected output: `Python 3.14.x`. If `python3.14` is not found, install Python 3.14 from the official Python website at https://www.python.org/downloads/ or via your platform's package manager, such as `brew install python@3.14` on macOS).*

2. **Create virtual environments and install dependencies:**
   Since virtual environments are not tracked by Git, initialize them using the verified `python3.14` interpreter:
   ```bash
   # For standalone MCP server:
   python3.14 -m venv campus-helpdesk/mcp-server/.venv
   campus-helpdesk/mcp-server/.venv/bin/pip install -r campus-helpdesk/mcp-server/requirements.txt

   # For plugin MCP server:
   python3.14 -m venv campus-helpdesk/plugin/campus-helpdesk/mcp-server/.venv
   campus-helpdesk/plugin/campus-helpdesk/mcp-server/.venv/bin/pip install -r campus-helpdesk/plugin/campus-helpdesk/mcp-server/requirements.txt
   ```

#### Step 3b: Launch and Verify
Execute using the dedicated virtual environment Python interpreter where the official MCP SDK is installed:
```bash
# Start standalone stdio server
campus-helpdesk/mcp-server/.venv/bin/python campus-helpdesk/mcp-server/server.py
```
Or run the full automated stdio protocol handshake:
```bash
campus-helpdesk/mcp-server/.venv/bin/python -c '
import subprocess, json
proc = subprocess.Popen(["campus-helpdesk/mcp-server/.venv/bin/python", "campus-helpdesk/mcp-server/server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
