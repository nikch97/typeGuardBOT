import ast
from pathlib import Path
from llm_client import generate_patch
#this file is for parsing python code
PROMPT_TEMPLATE = """You are a Python assistant that secures functions.
Task:
Given ONE Python function that uses type hints but has NO runtime type checks,
modify it by ADDING minimal isinstance() checks at the beginning of the function
for EACH annotated parameter.

STRICT RULES:
- You MUST add at least one isinstance() check.
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

#Detect functions with type-hinted parameters
def has_typed_params(func: ast.FunctionDef) -> bool:
    for arg in func.args.args:
        if arg.annotation is not None:
            return True
    return False

#Detect if a function has runtime type checks
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



# if __name__ == "__main__":
#     file_path = Path("../typechecking_project/sample.py")
#     funcs = parse_file(file_path)
#     for f in funcs:
#         print("Found function:", f.name)
#         if has_typed_params(f) and not function_has_type_check(f):
#             #print("Typed function:", f.name)
#             print("[SUSPECT] function missing runtime checks:", f.name)

if __name__ == "__main__":
    file_path = Path("typechecking_project/sample.py")
    code = file_path.read_text(encoding="utf-8")
    tree = ast.parse(code)
    collector = FuncCollector()
    collector.visit(tree)
    funcs = collector.functions

    suspects = []
    for f in funcs:
        if has_typed_params(f) and not function_has_type_check(f):
            suspects.append(f)
        if not suspects:
            print("No suspect functions found.")
        else:
            output_path = Path("patches.txt")
            with output_path.open("w", encoding="utf-8") as out:
                 for f in suspects:
                    print("=" * 80)
                    print("[SUSPECT]", f.name)
                    original = get_function_source(code, f)
                    print("Original:")
                    print(original)
                    print("-" * 80)
                    print("Asking LLM for patched version...")
                    patched = ask_llm_for_patch(original)
                    print("Patched:")
                    print(patched)

                    # write to file as well
                    out.write("=" * 80 + "\n")
                    out.write("[SUSPECT] " + f.name + "\n")
                    out.write("Original:\n" + original + "\n\n")
                    out.write("Patched:\n" + patched + "\n\n")
           


