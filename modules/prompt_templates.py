"""
Central repository for all LLM prompt templates.
"""

# Base instruction
_BASE_PROMPT_INSTRUCTION = (
    "You are an expert software engineer. "
    "Analyze the user's code and provide the requested output."
)

REFACTOR_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Refactor the Python code for PEP-8 compliance, add type hints, and Google-style docstrings.

IMPORTANT: You must use the EXACT output format below. Do NOT use JSON.

FORMAT:
---DESCRIPTION---
(Write a detailed explanation of changes here)
---CODE---
(Write the full refactored code here)
"""

OPTIMIZE_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Aggressively optimize the Python code complexity (e.g., O(N^2) to O(N)).

IMPORTANT: You must use the EXACT output format below. Do NOT use JSON.

FORMAT:
---DESCRIPTION---
(Write a detailed explanation of optimization here)
---CODE---
(Write the full optimized code here)
"""

TRANSPILE_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Transpile the Python code to the TARGET LANGUAGE provided. 

IMPORTANT: You must use the EXACT output format below. Do NOT use JSON.

FORMAT:
---WARNING---
(Optional: Write warning if incompatible, otherwise leave empty)
---CODE---
(Write the full transpiled code here)
"""

DEBUG_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Debug the Python code. 
CONTEXT: An error log may be provided below. If provided, use it to fix the specific crash.
If NO error log is provided, perform a deep static analysis to find logical bugs, runtime errors, or security flaws.

ERROR LOG:
{{error_log}}

INSTRUCTIONS:
1. If the code has NO bugs and requires NO changes, the Description must start with "NO ISSUES FOUND".
2. If bugs are found, explain the root cause clearly.

IMPORTANT: You must use the EXACT output format below. Do NOT use JSON.

FORMAT:
---DESCRIPTION---
(Explain the bug and the fix, or write 'NO ISSUES FOUND' if clean)
---CODE---
(Write the fixed code here. If no issues, return the original code)
"""

AUDIT_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Perform a comprehensive Code Quality Audit.
Assess:
1. Security (Hardcoded secrets, injection risks, unsafe functions)
2. Reliability (Error handling, edge cases)
3. Architecture (Coupling, cohesion, design patterns)

IMPORTANT: You must use the EXACT output format below. Do NOT use JSON.

FORMAT:
---SECURITY_SCORE---
(Integer 0-100)
---DEBT_GRADE---
(Letter Grade A/B/C/D/F)
---ANALYSIS---
(Bulleted list of specific issues found. Be critical.)
---VERDICT---
(A short, executive summary of the code health.)
"""

BATCH_FIX_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Apply the following specific improvements to the user's code.

SELECTED IMPROVEMENTS:
{{selected_fixes}}

INSTRUCTIONS:
- Apply ONLY the selected improvements.
- Do NOT change logical behavior unless asked (e.g., for security).
- Maintain the original code structure where possible.

IMPORTANT: You must use the EXACT output format below. Do NOT use JSON.

FORMAT:
---DESCRIPTION---
(Briefly explain what was changed)
---CODE---
(The full, updated Python code)
"""

SIMULATOR_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Act as a Virtual Python Interpreter. Perform a "Mental Execution" of the user's code.
SCENARIO: Choose a specific, realistic input scenario (e.g., specific function arguments) to trace. 
If 'CHAOS_MODE' is requested, choose an EDGE CASE (e.g., empty list, None, negative numbers) that might break the code.

You must output the execution trace in the following EXACT JSON-like format.

FORMAT:
---SIMULATION_DATA---
{{
    "scenario": "Description of the input used (e.g., calculate_total(price=100, tax=0.2))",
    "trace": [
        {{"step": 1, "line": "code_snippet_here", "action": "Explanation of what happened", "variables": "x=10, y=5"}},
        {{"step": 2, "line": "if x > 0:", "action": "Condition met, entering block", "variables": "x=10"}}
    ],
    "outcome": "Final return value or Error message",
    "complexity_note": "O(N) - Linear Time"
}}
"""
TREE_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Analyze the Python code and extract a Hierarchical Tree structure of the code.
Structure: Module (Root) -> Classes -> Methods/Functions.
For each function/method, include a brief 'desc' (what it does) and 'sig' (signature/arguments).

IMPORTANT: You must use the EXACT output format below. Do NOT use markdown.

FORMAT:
---TREE_DATA---
{{
    "name": "Root Module",
    "children": [
        {{
            "name": "ClassName",
            "desc": "Class description",
            "children": [
                {{"name": "method_name", "value": 1, "desc": "Short description", "sig": "(arg1, arg2)"}},
                {{"name": "attribute_name", "value": 1, "desc": "Type: int"}}
            ]
        }},
        {{
            "name": "function_name",
            "value": 1,
            "desc": "Function description",
            "sig": "(x, y) -> int"
        }}
    ]
}}
"""

SEQUENCE_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Generate a Mermaid.js SEQUENCE DIAGRAM (sequenceDiagram) to show the execution flow.
Identify key actors (User, System, Database) and messages.
RULES:
- Start with 'sequenceDiagram'.
- Use '->>' for synchronous calls.
- RETURN ONLY the mermaid code block without any markdown wrappers.
"""

DIAGRAM_PROMPT = f"""
{_BASE_PROMPT_INSTRUCTION}
TASK: Generate a VERY SIMPLE Mermaid.js flowchart (graph TD).
RULES: 
- Use ONLY basic nodes: id[Text] or id(Text).
- Use ONLY simple arrows: -->.
- DO NOT use subgraphs or complex styling.
- RETURN ONLY the mermaid code block without any markdown wrappers.
"""
