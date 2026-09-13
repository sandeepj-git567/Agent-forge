"""
Safe Code Analysis Tool for AgentForge AI

Performs static AST analysis, security auditing, and syntax validation.
NEVER executes code or arbitrary shell commands.
"""
import ast
from typing import Any

DANGEROUS_AST_NODES = {"Global", "Nonlocal", "Import", "ImportFrom"}
DANGEROUS_FUNCTIONS = {"eval", "exec", "os.system", "subprocess.Popen", "subprocess.run", "__import__"}


def safe_code_analysis(code: str) -> dict[str, Any]:
    """
    Perform safe static analysis of Python code snippets (FILE_ANALYSIS category).
    Does NOT execute the code.
    """
    if not code or not code.strip():
        return {"status": "error", "message": "Code string cannot be empty"}

    try:
        parsed_ast = ast.parse(code)
    except SyntaxError as e:
        return {
            "status": "syntax_error",
            "error": f"Syntax error at line {e.lineno}, col {e.offset}: {e.msg}",
            "valid_syntax": False
        }

    warnings: list[str] = []
    imports: list[str] = []
    functions_defined: list[str] = []
    classes_defined: list[str] = []

    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.FunctionDef):
            functions_defined.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes_defined.append(node.name)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_FUNCTIONS:
                warnings.append(f"Potentially dangerous function call detected: {node.func.id}()")
            elif isinstance(node.func, ast.Attribute) and f"{getattr(node.func.value, 'id', '')}.{node.func.attr}" in DANGEROUS_FUNCTIONS:
                warnings.append(f"Potentially dangerous method call detected: {node.func.attr}()")

    return {
        "status": "success",
        "valid_syntax": True,
        "metrics": {
            "num_lines": len(code.splitlines()),
            "functions": functions_defined,
            "classes": classes_defined,
            "imports": list(set(imports))
        },
        "security_warnings": warnings,
        "is_secure": len(warnings) == 0
    }
