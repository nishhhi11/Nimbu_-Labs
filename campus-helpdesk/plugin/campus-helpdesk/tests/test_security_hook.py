#!/usr/bin/env python3
"""
Unit tests for campus-helpdesk PreToolUse security hook.
Tests realistic Antigravity PreToolUse payloads against security_hook.py.
Verifies:
1. Safe commands are allowed (exit code 0, decision: "allow").
2. Ordinary text containing 'password' or 'token' is allowed (no false positives).
3. Genuinely dangerous commands (e.g. 'rm -rf /', '/etc/shadow', fork bomb) are denied (exit code 0, decision: "deny").
4. Path traversals in file operations are denied.
"""

import json
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parent.parent / "hooks" / "security_hook.py"


def run_hook(payload: dict) -> tuple:
    proc = subprocess.Popen(
        [sys.executable, str(HOOK_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate(input=json.dumps(payload))
    return proc.returncode, stdout.strip(), stderr.strip()


def test_safe_command():
    payload = {
        "conversationId": "test-convo-1234",
        "stepIdx": 10,
        "toolCall": {
            "name": "run_command",
            "args": {
                "CommandLine": "python3 ./skills/timetable-helper/scripts/timetable_helper.py --batch CS-A --day Monday"
            }
        }
    }
    code, stdout, stderr = run_hook(payload)
    assert code == 0, f"Expected exit code 0, got {code}"
    res = json.loads(stdout)
    assert res.get("decision") == "allow", f"Expected allow, got {res}"
    print("✓ Safe command test passed")


def test_benign_words_password_and_token():
    payload = {
        "conversationId": "test-convo-1234",
        "stepIdx": 11,
        "toolCall": {
            "name": "run_command",
            "args": {
                "CommandLine": "echo 'Please reset your campus portal password using your security token' > instructions.txt"
            }
        }
    }
    code, stdout, stderr = run_hook(payload)
    assert code == 0, f"Expected exit code 0, got {code}"
    res = json.loads(stdout)
    assert res.get("decision") == "allow", f"Expected allow for benign 'password' and 'token', got {res}"
    print("✓ Benign password & token check passed (no false positives)")


def test_dangerous_destructive_command():
    payload = {
        "conversationId": "test-convo-1234",
        "stepIdx": 12,
        "toolCall": {
            "name": "run_command",
            "args": {
                "CommandLine": "rm -rf /var/log/*"
            }
        }
    }
    code, stdout, stderr = run_hook(payload)
    assert code == 0, f"Expected exit code 0, got {code}"
    res = json.loads(stdout)
    assert res.get("decision") == "deny", f"Expected deny, got {res}"
    assert "reason" in res, "Expected reason in deny response"
    print("✓ Genuinely dangerous command (rm -rf) blocked with code 0")


def test_sensitive_path_access():
    payload = {
        "conversationId": "test-convo-1234",
        "stepIdx": 13,
        "toolCall": {
            "name": "run_command",
            "args": {
                "CommandLine": "cat /etc/shadow"
            }
        }
    }
    code, stdout, stderr = run_hook(payload)
    assert code == 0, f"Expected exit code 0, got {code}"
    res = json.loads(stdout)
    assert res.get("decision") == "deny", f"Expected deny, got {res}"
    print("✓ Sensitive path access (/etc/shadow) blocked with code 0")


def test_path_traversal_in_file_tool():
    payload = {
        "conversationId": "test-convo-1234",
        "stepIdx": 14,
        "toolCall": {
            "name": "read_file",
            "args": {
                "Path": "../../.ssh/id_rsa"
            }
        }
    }
    code, stdout, stderr = run_hook(payload)
    assert code == 0, f"Expected exit code 0, got {code}"
    res = json.loads(stdout)
    assert res.get("decision") == "deny", f"Expected deny, got {res}"
    print("✓ File path traversal (../../.ssh/id_rsa) blocked with code 0")


if __name__ == "__main__":
    print("Running security hook tests...")
    test_safe_command()
    test_benign_words_password_and_token()
    test_dangerous_destructive_command()
    test_sensitive_path_access()
    test_path_traversal_in_file_tool()
    print("All security hook tests passed successfully!")

