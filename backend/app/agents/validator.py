import ast
import os
import re
import time
from typing import Dict, Any, List
from app.agents.state import AgentState
from app.services.logger_service import log_agent_step

ALLOWED_IMPORTS = {
    "pandas", "pd",
    "numpy", "np",
    "matplotlib", "plt", "matplotlib.pyplot",
    "seaborn", "sns",
    "scipy", "stats",
    "sklearn",
    "math", "json", "datetime", "re", "io"
}

FORBIDDEN_KEYWORDS = [
    "os.system", "os.popen", "os.exec", "os.spawn", "os.remove", "os.unlink", "os.rmdir", "os.makedirs",
    "subprocess", "eval", "exec", "socket", "requests", "urllib", "ctypes", "pty", "shutil.rmtree"
]

class CodeSecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_module = alias.name.split('.')[0]
            if base_module not in ALLOWED_IMPORTS:
                self.errors.append(f"Forbidden import '{alias.name}' detected.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module not in ALLOWED_IMPORTS:
                self.errors.append(f"Forbidden import from '{node.module}' detected.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # 1. Check direct function calls like eval(), exec(), open()
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in {"eval", "exec", "__import__", "compile", "globals", "locals"}:
                self.errors.append(f"Forbidden function call '{func_name}()' detected.")
            elif func_name in {"open", "file"}:
                # Check path argument for open()
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    path_str = node.args[0].value
                    if self._is_path_traversal(path_str):
                        self.errors.append(f"Path traversal access '{path_str}' rejected.")

        # 2. Check attribute calls like os.system(), subprocess.run(), Path(...)
        elif isinstance(node.func, ast.Attribute):
            full_call = self._get_attribute_name(node.func)
            if any(forbidden in full_call.lower() for forbidden in ["system", "popen", "subprocess", "socket", "eval", "exec", "requests", "urllib", "rmtree", "unlink", "remove"]):
                self.errors.append(f"Forbidden operation '{full_call}()' detected.")

        # 3. Check arguments for path traversal strings
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if self._is_path_traversal(arg.value):
                    self.errors.append(f"Path traversal or prohibited file access '{arg.value}' detected.")

        self.generic_visit(node)

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return node.attr

    def _is_path_traversal(self, path_str: str) -> bool:
        """
        Rejects paths containing directory traversal (..) or system root directories outside workspace.
        """
        if not path_str or not isinstance(path_str, str):
            return False
        
        # Check for path traversal dots
        if ".." in path_str:
            return True

        # Check for absolute system paths (e.g. /etc/, /var/, /usr/, C:\Windows, C:\System32)
        lowered = path_str.lower()
        system_roots = ["/etc/", "/var/", "/usr/", "/root/", "/proc/", "/sys/", "c:\\windows", "c:\\system32", "c:\\users\\"]
        for sys_root in system_roots:
            if lowered.startswith(sys_root) and "autonomous-data-analysis-agent" not in lowered:
                return True
        return False

def validate_code(code: str) -> Dict[str, Any]:
    """
    Validates Python code AST for dangerous imports, system execution, or file/network exploits.
    """
    if not code or not code.strip():
        return {"valid": False, "errors": ["Generated code is empty."]}

    # Check for direct raw text forbidden keywords as secondary check
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", code):
            return {"valid": False, "errors": [f"Forbidden keyword '{kw}' detected in code."]}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"valid": False, "errors": [f"Syntax error in generated code: {str(e)}"]}

    visitor = CodeSecurityVisitor()
    visitor.visit(tree)

    if visitor.errors:
        return {"valid": False, "errors": visitor.errors}

    return {"valid": True, "errors": []}

def validate_code_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Validating generated Python code using AST security checks.
    """
    start_time = time.time()
    analysis_id = state.get("dataset_id") or "unknown_analysis"
    retry_count = state.get("retry_count", 0)

    code = state.get("generated_code", "")
    val_res = validate_code(code)

    duration_ms = (time.time() - start_time) * 1000

    if val_res["valid"]:
        log_agent_step(analysis_id, "validator", "completed", duration_ms, retry_count)
        return {
            "validated_code": code,
            "status": "code_validated"
        }
    else:
        err_msg = f"Security Validation Failed: {'; '.join(val_res['errors'])}"
        log_agent_step(analysis_id, "validator", "validation_failed", duration_ms, retry_count, err_msg)
        return {
            "validated_code": None,
            "execution_error": err_msg,
            "status": "validation_failed"
        }
