import xml.etree.ElementTree as ET
import os
from collections import defaultdict

PMD_FILE = "java-project/target/pmd.xml"
CHECKSTYLE_FILE = "java-project/target/checkstyle-result.xml"
SPOTBUGS_FILE = "java-project/target/spotbugsXml.xml"


def is_output_file(path):
    if not path:
        return False

    normalized = path.replace("\\", "/").lower().strip()
    return "/output/" in normalized or normalized.endswith("output/sample.java")


IGNORE_PMD_RULES = {
    "AtLeastOneConstructor",
    "OnlyOneReturn",
    "ShortVariable",
    "LongVariable",
    "DefaultPackage",
    "MethodArgumentCouldBeFinal",
    "LocalVariableCouldBeFinal",
    "FormalParameterCouldBeFinal",
    "CommentDefaultAccessModifier",
}


def summarize():
    issues = defaultdict(list)

    #-------- PMD --------
    if os.path.exists(PMD_FILE):
        try:
            tree = ET.parse(PMD_FILE)
            root = tree.getroot()
            ns = {"pmd": "http://pmd.sourceforge.net/report/2.0.0"}

            for file in root.findall("pmd:file", ns):
                file_name = file.get("name")
                if not is_output_file(file_name):
                    continue

                for violation in file.findall("pmd:violation", ns):
                    rule = violation.get("rule", "PMD Issue")
                    if rule in IGNORE_PMD_RULES:
                        continue
                    line = violation.get("beginline")
                    issues[f"{rule} (PMD)"].append(line)

        except Exception as e:
            print("PMD parse error:", e)

    # -------- CHECKSTYLE --------
    if os.path.exists(CHECKSTYLE_FILE):
        try:
            tree = ET.parse(CHECKSTYLE_FILE)
            root = tree.getroot()

            for file in root.findall("file"):
                file_name = file.get("name")
                if not is_output_file(file_name):
                    continue

                for error in file.findall("error"):
                    source = error.get("source")
                    line = error.get("line")
                    rule = source.split(".")[-1] if source else "Checkstyle Issue"
                    issues[f"{rule} (Checkstyle)"].append(line)

        except Exception as e:
            print("Checkstyle parse error:", e)

    # -------- SPOTBUGS --------
    if os.path.exists(SPOTBUGS_FILE):
        try:
            tree = ET.parse(SPOTBUGS_FILE)
            root = tree.getroot()

            for bug in root.findall(".//BugInstance"):
                bug_type = bug.get("type", "SpotBugs Issue")

                line = None
                source_path = None

                source_line = bug.find(".//SourceLine")
                if source_line is not None:
                    line = source_line.get("start")
                    source_path = source_line.get("sourcepath")

                if not is_output_file(source_path):
                    continue

                issues[f"{bug_type} (SpotBugs)"].append(line)

        except Exception as e:
            print("SpotBugs parse error:", e)

    # -------- BUILD SUMMARY --------
    pmd_lines = []
    spotbugs_lines = []
    checkstyle_lines = []

    for issue, lines in issues.items():
        valid_lines = [str(l) for l in lines if l]
        count = len(valid_lines) if valid_lines else len(lines)

        formatted = f"- {issue}: {count} occurrences"

        if "(PMD)" in issue:
            pmd_lines.append(formatted)
        elif "(Checkstyle)" in issue:
            checkstyle_lines.append(formatted)
        elif "(SpotBugs)" in issue:
            spotbugs_lines.append(formatted)

    summary_lines = spotbugs_lines + pmd_lines + checkstyle_lines

    if not summary_lines:
        return "✅ No issues found."

    return "\n".join(summary_lines)