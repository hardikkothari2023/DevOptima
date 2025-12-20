"""
Handles the generation and rendering of Mermaid.js architecture diagrams.

This module uses the LLM handler to generate Mermaid syntax from Python code
and provides a utility to display the diagram in a Streamlit application.
"""

import streamlit as st
from streamlit_mermaid import st_mermaid
from modules.llm_handler import call_groq_api
from modules.prompt_templates import DIAGRAM_PROMPT

def generate_mermaid_diagram(python_code: str) -> str:
    """
    Generates a Mermaid.js diagram syntax from Python code using the LLM.

    Args:
        python_code: The Python code to analyze.

    Returns:
        The Mermaid.js diagram syntax as a string, or an error message.
    """
    if not python_code.strip():
        return "ERROR: Cannot generate diagram from empty code."

    # Call the LLM with the specific diagram generation prompt
    mermaid_syntax = call_groq_api(
        system_prompt=DIAGRAM_PROMPT,
        user_code=python_code
    )
    return mermaid_syntax

def render_mermaid_diagram(mermaid_code: str):
    """
    Renders a Mermaid.js diagram in the Streamlit UI.

    Handles gracefully if the input is an error message instead of valid syntax.

    Args:
        mermaid_code: The Mermaid.js syntax to render.
    """
    if "ERROR:" in mermaid_code or not mermaid_code.strip():
        st.error(f"Could not generate the architecture diagram. Details: {mermaid_code}")
    else:
        st.subheader("Generated Architecture Diagram")
        with st.container(border=True):
            st_mermaid(mermaid_code, height="600px")


