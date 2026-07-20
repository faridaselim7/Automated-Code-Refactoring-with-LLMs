# SAFIR: Static Analysis Feedback for Iterative Code Refactoring

SAFIR is an automated Java code-refactoring framework that combines Large Language Model generation with compilation validation and static analysis feedback.

Instead of accepting a single LLM-generated refactoring, SAFIR evaluates the generated code and iteratively guides the model using violations detected by three static analysis tools: PMD, Checkstyle, and SpotBugs.

This repository contains the implementation developed for the research paper:

> **Automated Code Refactoring with Large Language Models**

## Overview

Code refactoring improves the internal structure, readability, and maintainability of software without changing its intended behavior.

Traditional static analysis tools can reliably detect code smells, style violations, and possible defects. However, they usually report problems without generating context-aware fixes.

Large Language Models can generate complete refactored implementations, but their output may contain:

- Syntax or compilation errors
- Hallucinated modifications
- Coding-standard violations
- New code smells or potential defects

SAFIR combines the strengths of both approaches. The LLM generates the refactored code, while deterministic tools validate the output and provide structured feedback for further improvement.

## Framework Workflow

SAFIR follows an iterative refactoring process:

1. The original Java code is inserted into an initial refactoring prompt.
2. The prompt is sent to DeepSeek-Coder-V2-Lite-Instruct.
3. The model generates a refactored version.
4. The generated code is compiled.
5. If compilation fails:
   - Compiler errors are extracted.
   - A syntax-repair prompt is created.
   - The LLM attempts to repair the code.
6. If compilation succeeds:
   - PMD detects code smells and maintainability issues.
   - Checkstyle detects formatting and coding-standard violations.
   - SpotBugs detects possible runtime and bytecode-level defects.
7. The analysis reports are converted into structured feedback.
8. The feedback is sent to the LLM for another refinement iteration.
9. The best valid version is retained as the final output.

The pipeline performs a maximum of three refinement iterations.

## Main Components

### Refactoring Model

SAFIR primarily uses:

```text
DeepSeek-Coder-V2-Lite-Instruct
```

The model is executed locally using Ollama.

### PMD

PMD analyzes Java source code for maintainability and structural issues, such as:

- Unused code
- Complex methods
- Redundant control flow
- Poor design patterns
- Unnecessary object creation
- Code smells

### Checkstyle

Checkstyle checks compliance with Java coding standards, including:

- Naming conventions
- Braces
- Whitespace
- Indentation
- Import organization
- Formatting consistency

### SpotBugs

SpotBugs analyzes compiled Java bytecode for possible defects, including:

- Null-pointer risks
- Resource-management problems
- Incorrect API usage
- Concurrency issues
- Bug-prone patterns

## Project Requirements

The following software is required:

- Python 3
- Java Development Kit 17
- Apache Maven
- Ollama

Verify the installations:

```bash
python --version
java -version
mvn -version
ollama --version
```

## Python Dependency

Install the required Python package:

```bash
pip install requests
```

## Ollama Model

The project is configured to use:

```text
mannix/deepseek-coder-v2-lite-instruct:q5_0
```

Pull the model using:

```bash
ollama pull mannix/deepseek-coder-v2-lite-instruct:q5_0
```

Confirm that it is installed:

```bash
ollama list
```

Ollama should be available locally at:

```text
http://localhost:11434
```

## Maven Configuration

The current implementation contains a Windows-specific Maven path inside `scripts/refactor.py`:

```python
MAVEN_CMD = r"C:\Program Files\apache-maven-3.9.11\bin\mvn.cmd"
```

Update this value when Maven is installed in a different location.

For example:

```python
MAVEN_CMD = r"C:\apache-maven\bin\mvn.cmd"
```

## Adding Input Code

Open:

```text
java-project/src/main/java/input/Sample.java
```

Place the Java class or code that should be refactored inside this file.

Example:

```java
package input;

public class Sample {
    public boolean isSpecial(String value) {
        if (value == "special") {
            return true;
        }

        return false;
    }
}
```

The pipeline automatically changes the generated version to the `output` package.

## Running the Pipeline

Open a terminal in the main project directory—the folder containing both `scripts` and `java-project`.

Run:

```bash
python scripts/refactor.py
```

Do not run the command from inside the `scripts` directory because the program uses paths relative to the main project folder.

## Generated Output

The final refactored Java code is saved to:

```text
java-project/src/main/java/output/Sample.java
```

A text report is saved to:

```text
results/single_pipeline_report.txt
```

The report includes:

- Final output path
- Best detected issue count
- Final static analysis summary
- Final refactored Java code

## Static Analysis

The pipeline internally executes the equivalent of:

```bash
mvn clean compile pmd:pmd checkstyle:checkstyle spotbugs:spotbugs
```

The generated XML reports are stored in the Maven `target` directory and parsed by `summarize_reports.py`.

## Research Results

The complete SAFIR research evaluation reported:

| Metric | Result |
| Pipeline Average Code Smell Reduction Rate | 30.9% |
| LLM-only Average Code Smell Reduction Rate | 20.0% |
