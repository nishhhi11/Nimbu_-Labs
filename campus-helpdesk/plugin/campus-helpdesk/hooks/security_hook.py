#!/usr/bin/env python3
"""
security_hook.py
PreToolUse security hook for the campus-helpdesk plugin.
Complies with Antigravity Plugin Hook specifications:
- Reads event context payload as JSON from standard input.
- Inspects the toolCall (name and arguments).
- Blocks dangerous shell operations or directory traversal attempts on command lines / paths.
- Allows ordinary text containing words like 'password' or 'token' without broad substring false positives.
- Returns a JSON response containing {"decision": "allow"} or {"decision": "deny", "reason": "..."}.
- Always exits with returncode 0.
"""

import sys
import json
import re

# Targeted patterns for dangerous shell commands or argument flags
DANGEROUS_COMMAND_PATTERNS = [
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b",       # rm -rf, rm -fr, etc.
    r"\bmkfs\b",                             # filesystem format
    r"\bdd\s+if=",                           # raw block writes
    r">\s*/dev/sd[a-z]",                     # raw device overwrite
    r"\bshutdown\b",                         # system shutdown
    r"\breboot\b",                           # reboot
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\};\s*:", # fork bomb
]

# Sensitive system paths / credentials to prevent unauthorized traversal or leaking
SENSITIVE_PATH_PATTERNS = [
    r"(?:^|[\s/\"'])\.\.(?:/|[\s\"']|$)",   # path traversal like ../ or /..
    r"/etc/(?:shadow|passwd|sudoers)",      # sensitive Unix system files
    r"~?/\.ssh(?:/|$)",                     # SSH keys and configs
    r"id_rsa(?:\.pub)?",                    # SSH private/public key files
    r"(?:^|/)\.env(?:\.[a-zA-Z0-9_-]+)?$",  # environment secret files
    r"/root(?:/|$)",                        # root home directory
]


def check_command_safety(cmd_str: str) -> tuple:
    """Validate a shell command string for dangerous operations or sensitive path accesses."""
    for pattern in DANGEROUS_COMMAND_PATTERNS:
        if re.search(pattern, cmd_str, re.IGNORECASE):
            return False, f"Potentially destructive system command detected matching pattern: {pattern}"

    for pattern in SENSITIVE_PATH_PATTERNS:
        if re.search(pattern, cmd_str):
            return False, f"Access to sensitive path or traversal detected matching pattern: {pattern}"

    return True, ""


def check_path_safety(path_str: str) -> tuple:
    """Validate a file path argument."""
    for pattern in SENSITIVE_PATH_PATTERNS:
        if re.search(pattern, path_str):
            return False, f"Access to sensitive path or traversal detected matching pattern: {pattern}"
    return True, ""


def validate_tool_call(tool_call: dict) -> tuple:
    """Inspect toolCall object according to Antigravity PreToolUse contract."""
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {}) or {}

    if not isinstance(args, dict):
        return True, ""

    # Inspect command line executions
    if tool_name == "run_command" or "CommandLine" in args or "command" in args:
        cmd = args.get("CommandLine") or args.get("command") or ""
        if isinstance(cmd, str):
            is_safe, reason = check_command_safety(cmd)
            if not is_safe:
                return False, reason

    # Inspect file operations (read_file, edit_file, write_file, etc.)
    for path_key in ("Path", "path", "file_path", "filePath"):
        if path_key in args:
            target_path = args.get(path_key)
            if isinstance(target_path, str):
                is_safe, reason = check_path_safety(target_path)
                if not is_safe:
                    return False, reason

    return True, ""


def main():
    try:
        input_raw = sys.stdin.read().strip()
        if not input_raw:
            print(json.dumps({"decision": "allow"}))
            sys.exit(0)

        payload = json.loads(input_raw)

        # Documented Antigravity PreToolUse payload format:
        # { "toolCall": { "name": "...", "args": { ... } }, "stepIdx": ... }
        tool_call = payload.get("toolCall")
        if not tool_call or not isinstance(tool_call, dict):
            # Fallback if args passed at root or under arguments/input
            tool_name = payload.get("name", "")
            args = payload.get("args") or payload.get("arguments") or payload.get("input") or {}
            tool_call = {"name": tool_name, "args": args}

        is_safe, reason = validate_tool_call(tool_call)

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
        # Exit 0 with deny response on parsing/validation error
        print(json.dumps({"decision": "deny", "reason": f"Hook validation error: {str(e)}"}))
        sys.exit(0)


if __name__ == "__main__":
    main()
