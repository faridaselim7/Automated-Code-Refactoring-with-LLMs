import re

OUTPUT_PATH = "java-project/src/main/java/output/Sample.java"


def read_output_code():
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def write_output_code(code):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(code)


def clean_code(code: str) -> str:
    if not isinstance(code, str):
        return ""

    code = code.replace("```java", "")
    code = code.replace("```", "")
    return code.strip()

def build_feedback_prompt(summary):
    code = read_output_code()

    return f"""
You are an expert Java code repair assistant.

The following static analysis issues were detected:

{summary}

Task:
Fix ONLY the listed issues with the SMALLEST POSSIBLE CHANGES.

Rules:
1. Preserve behavior exactly.
2. Preserve all side effects and control flow.
3. Do not rewrite unrelated parts of the code.
4. Do not introduce new methods, fields, or classes unless absolutely necessary.
5. Avoid introducing any new static analysis issues.
6. If an issue cannot be fixed safely without changing behavior, leave that part unchanged.
7. Keep the code structure as close as possible to the current version.
8. The code must compile.
9. Return ONLY valid Java code.
10. Do not add explanations or comments.

Code:
{code}
""".strip()

def build_syntax_recovery_prompt(compiler_errors):
    code = read_output_code()

    return f"""
You are an expert Java syntax repair assistant.

The following Java code contains compilation or syntax errors:

{compiler_errors}

Fix ONLY the syntax and compilation issues.
- Preserve functionality
- Do NOT make unnecessary refactoring changes
- Return ONLY valid Java code
- Do not add explanations
- Do not add comments

Code:
{code}
""".strip()