#!/usr/bin/env python3
"""
security_hook.py
PreToolUse security hook for the campus-helpdesk plugin.
Complies with Antigravity Plugin Hook specifications:
- Reads event context payload as JSON from standard input.
- Validates the tool and arguments.
- Returns a JSON response containing {"decision": "allow"} or {"decision": "deny", "reason": "..."}.
- Exits with returncode 0 so the orchestrator processes the denial decision properly.
"""

import sys
import json

BLOCKED_PATTERNS = [
    "..",
    "/etc",
    "/root",
    "~/.ssh",
    "id_rsa",
    ".env",
    "token",
    "password",
    "rm -rf"
]


def validate_input_data(data) -> tuple:
    serialized = json.dumps(data)
    for pattern in BLOCKED_PATTERNS:
        if pattern in serialized:
            return False, f"Hazardous path or token pattern detected: '{pattern}'"
    return True, ""


def main():
    try:
        input_raw = sys.stdin.read().strip()
        if not input_raw:
            if len(sys.argv) > 1:
                test_arg = " ".join(sys.argv[1:])
                is_safe, reason = validate_input_data(test_arg)
                if not is_safe:
                    print(json.dumps({"decision": "deny", "reason": reason}))
                    sys.exit(0)
            print(json.dumps({"decision": "allow"}))
            sys.exit(0)

        payload = json.loads(input_raw)
        tool_args = payload.get("arguments", {}) or payload.get("input", {}) or payload
        is_safe, reason = validate_input_data(tool_args)
        
        if not is_safe:
            response = {
                "decision": "deny",
                "reason": f"[SECURITY POLICY VIOLATION] Access denied by campus-helpdesk security hook: {reason}"
            }
            print(json.dumps(response))
            sys.exit(0)

        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"decision": "deny", "reason": f"Hook validation error: {str(e)}"}))
        sys.exit(0)


if __name__ == "__main__":
    main()
