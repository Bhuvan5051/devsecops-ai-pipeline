import ast
import sys
import os

PROMPT_VAR_NAMES = {"SYSTEM_PROMPT", "system_prompt", "SYSTEM_MESSAGE", "system_message"}
INJECTION_PHRASES = [
    "ignore previous instructions",
    "you are now",
    "pretend you are",
    "act as if you have no restrictions",
]

issues = []

for root, _, files in os.walk("."):
    for file in files:
        if file.endswith(".py") and file != "inject_scanner.py":
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            for phrase in INJECTION_PHRASES:
                if phrase in content.lower():
                    issues.append(f"{filepath} — injection phrase found: '{phrase}'")

            try:
                tree = ast.parse(content, filename=filepath)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id in PROMPT_VAR_NAMES:
                                issues.append(f"{filepath}:{node.lineno} — hardcoded system prompt variable '{target.id}'")
            except SyntaxError:
                pass

if issues:
    print("PROMPT INJECTION SCANNER: FAIL\n")
    for issue in issues:
        print(f"  {issue}")
    sys.exit(1)

print("PROMPT INJECTION SCANNER: PASS — No hardcoded system prompts or injection phrases found.")
sys.exit(0)
