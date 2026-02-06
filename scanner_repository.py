import ast
import sys
from pathlib import Path

from llm_client import generate_patch

# This file is for parsing python code
PROMPT_TEMPLATE = """You are a Python assistant that secures functions.
Task:
Given ONE Python function that uses type hints but has NO runtime type checks,
modify it by ADDING minimal isinstance() checks at the beginning of the function
for EACH annotated parameter.

STRICT RULES:
- You MUST add at least one isinstance() check.
- Output ONLY the patched function.
- Do NOT add example calls, tests, decorators, or explanations.
- Do NOT print anything extra.
- Return ONLY the modified function.
- Wrap your answer in a single ```python code block.

Original function:
```python
{func_code}
```
Patched function:
"""

# This is for checking a folder

SKIP_DIRS = {".git", "__pycache__", "venv", ".venv", ".mypy_cache"}

def iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        # skip unwanted directories 
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path

class FuncCollector(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions.append(node)
        self.generic_visit(node)


def parse_file(path: Path):
    code = path.read_text(encoding="utf-8")
    tree = ast.parse(code)
    collector = FuncCollector()
    collector.visit(tree)
    return collector.functions

# Detect functions with type-hinted parameters

def has_typed_params(func: ast.FunctionDef) -> bool:
    for arg in func.args.args:
      if arg.annotation is not None:
        return True
    return False

# Detect if a function has runtime type checks

TYPE_CHECK_FUNCS = {"isinstance"}  # we can add more later

def function_has_type_check(func: ast.FunctionDef) -> bool:
    param_names = {arg.arg for arg in func.args.args}
    for node in ast.walk(func):
        # isinstance(x, ...)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in TYPE_CHECK_FUNCS and node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Name) and first_arg.id in param_names:
                    return True
    return False
  

def get_function_source(code: str, func: ast.FunctionDef) -> str:
    lines = code.splitlines()
    start = func.lineno - 1
    end = func.end_lineno
    return "\n".join(lines[start:end])

def ask_llm_for_patch(func_code: str) -> str:
    prompt = PROMPT_TEMPLATE.format(func_code=func_code)
    patch = generate_patch(prompt)
    return patch

def analyze_file(path: Path, out_handle):
    """Scan a single file and write suspect functions + patches to out_handle."""
    code = path.read_text(encoding="utf-8")
    tree = ast.parse(code)
    collector = FuncCollector()
    collector.visit(tree)
    funcs = collector.functions
    for f in funcs:
        if has_typed_params(f) and not function_has_type_check(f):
            original = get_function_source(code, f)
            patched = ask_llm_for_patch(original).strip()

            print("=" * 80, file=out_handle)
            print(f"[FILE] {path}", file=out_handle)
            print(f"[SUSPECT] {f.name}", file=out_handle)
            print("Original:", file=out_handle)
            print(original, file=out_handle)
            print("\nPatched:", file=out_handle)
            print(patched, file=out_handle)
            print(file=out_handle)
        
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scanner.py /content/copytype.py")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    output_path = Path("patches.txt")

    with output_path.open("w", encoding="utf-8") as out:
        for py_file in iter_python_files(root):
            analyze_file(py_file, out)

    print(f"Done. Results saved to {output_path}")
