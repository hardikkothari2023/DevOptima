"""
Provides functions for parsing and validating Python code.

This module uses Python's built-in Abstract Syntax Tree (AST) module
to safely parse code without executing it. This is a critical security
and quality-control measure before sending code to the LLM.
"""

import ast

def validate_python_code(code: str) -> str | None:
    """
    Validates Python code using AST parsing.

    Args:
        code: A string containing Python code.

    Returns:
        None if the code is valid Python syntax.
        An error message string if the code has a syntax error.
    """
    try:
        ast.parse(code)
        return None  # Code is syntactically valid
    except SyntaxError as e:
        return f"Syntax Error: {e.msg} on line {e.lineno}"
    except Exception as e:
        return f"An unexpected validation error occurred: {e}"
