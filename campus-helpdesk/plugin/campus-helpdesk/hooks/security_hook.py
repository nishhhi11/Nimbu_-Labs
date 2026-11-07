#!/usr/bin/env python3
"""
security_pre_command_hook.py
Security hook for the campus-helpdesk plugin.
Validates file access and tool executions to prevent path traversal and arbitrary command execution.
"""

import sys
import os

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


def validate_input(command_or_path: str) -> bool:
    for pattern in BLOCKED_PATTERNS:
        if pattern in command_or_path:
            return False
    return True


def main():
    if len(sys.argv) > 1:
        target = " ".join(sys.argv[1:])
        if not validate_input(target):
            print(f"[SECURITY BLOCKED] Disallowed target or hazardous pattern detected: '{target}'", file=sys.stderr)
            sys.exit(1)
    # Passed security inspection
    sys.exit(0)


if __name__ == "__main__":
    main()

