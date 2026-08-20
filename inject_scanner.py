#!/usr/bin/env python3
"""
inject_scanner.py

Custom Gate 4 scanner for Project 5 (DevSecOps + AI Security Gates).

Scans every .py file in the repository for:
  - Hardcoded system prompt assignments (SYSTEM_PROMPT =, system_message =, "role": "system")
  - Common prompt-injection bypass phrases that should never appear
    hardcoded in application source (these belong in system-level guardrails,
    not as literal strings an attacker could also match/exploit)

Exit code 1 if any match is found (fails the pipeline).
Exit code 0 if clean.
"""

import os
import re
import sys

# Patterns that indicate a hardcoded system prompt / role definition
SYSTEM_PROMPT_PATTERNS = [
    r"SYSTEM_PROMPT\s*=",
    r"system_message\s*=",
    r"[\"']role[\"']\s*:\s*[\"']system[\"']",
]

# Known prompt-injection bypass phrases
INJECTION_PHRASES = [
    "ignore previous instructions",
    "you are now",
    "pretend you are",
    "act as if you have no restrictions",
]

SCAN_EXTENSIONS = (".py",)
EXCLUDE_DIRS = {".git", ".github", "venv", "__pycache__", "node_modules"}


def find_python_files(root="."):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if filename.endswith(SCAN_EXTENSIONS):
                yield os.path.join(dirpath, filename)


def scan_file(filepath):
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                for pattern in SYSTEM_PROMPT_PATTERNS:
                    if re.search(pattern, line):
                        findings.append(
                            (filepath, lineno, "hardcoded system prompt", line.strip())
                        )
                lower_line = line.lower()
                for phrase in INJECTION_PHRASES:
                    if phrase in lower_line:
                        findings.append(
                            (filepath, lineno, f"injection phrase: '{phrase}'", line.strip())
                        )
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [warn] could not read {filepath}: {e}", file=sys.stderr)
    return findings


def main():
    all_findings = []
    for py_file in find_python_files("."):
        all_findings.extend(scan_file(py_file))

    if all_findings:
        print("PROMPT INJECTION SCANNER: FAIL\n")
        print(f"Found {len(all_findings)} issue(s):\n")
        for filepath, lineno, reason, snippet in all_findings:
            print(f"  {filepath}:{lineno} — {reason}")
            print(f"      {snippet}")
        print("\nRemove hardcoded system prompts and injection-bypass phrases")
        print("from source. System prompts belong in environment variables or")
        print("a secrets manager, not literal strings in application code.")
        sys.exit(1)
    else:
        print("PROMPT INJECTION SCANNER: PASS")
        print("No hardcoded system prompts or injection phrases found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
