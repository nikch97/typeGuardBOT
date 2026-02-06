Here is a **clean, GitHub-ready `README.md`** based directly on your report. You can copy-paste this as is.

---

# TypeGuardBot

**Detecting Missing Runtime Type Validation in Python Using LLMs**

## Overview

TypeGuardBot is a static analysis and automated patching tool designed to improve the safety of Python codebases that use **gradual typing**. While Python allows developers to annotate function parameters with type hints, these types are not enforced at runtime. This can lead to runtime errors, unexpected behavior, or security issues when invalid inputs are passed.

TypeGuardBot detects such cases and uses a Large Language Model (LLM) to automatically generate runtime type checks.

---

## Project Structure

```
.
├── typechecking_project/   # Target Python files or repositories to analyze
├── scanner.py              # Main analysis and patch-generation script
├── llm_client.py           # LLM interface for generating patches
├── patches.txt             # Output file containing before/after patches
└── README.md
```

---

## How It Works

1. **Recursive Scanning**
   The tool scans all `.py` files in a given directory, excluding folders such as `.git`, `venv`, and `__pycache__`.

2. **Static Code Analysis**
   Each file is parsed using Python’s AST to extract function definitions.

3. **Detection of Unsafe Functions**
   Functions are flagged if they:

   * Have type-annotated parameters, and
   * Do not contain runtime type checks (e.g., `isinstance()`).

4. **LLM-Based Patching**
   The source code of each unsafe function is sent to an LLM, which generates a patched version with appropriate runtime checks.

5. **Result Logging**
   All results are written to `patches.txt`, including both original and patched versions.

---

## Output (`patches.txt`)

For each detected unsafe function, `patches.txt` includes:

* File path
* Function name
* Original function source code
* LLM-generated patched version with `isinstance()` checks
* Clear separators between entries

---

## LLM Model

The project uses **StarCoder2-3B**, an open-source 3-billion-parameter code generation model from the BigCode project.
The model is run on **Google Colab with GPU** to generate consistent and structured Python code patches.

---

## Usage

```bash
python scanner.py /path/to/python/project
```

After execution, all detected issues and patches will be saved to `patches.txt`.

---

## Notes

* Two versions of the scanner were implemented:

  * Single-file analysis
  * Full project (repository) analysis
* The tool was tested on a Python repository with ~40 files and produced successful results.
* This project serves as a foundation for future work on evaluating different LLMs and improving patch quality.

---
