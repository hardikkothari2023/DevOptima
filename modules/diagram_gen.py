"""
Handles the generation and rendering of architecture diagrams and hierarchical trees.
"""

import streamlit as st
import json
from streamlit_mermaid import st_mermaid
from streamlit_echarts import st_echarts
from modules.llm_handler import call_groq_api
from modules.prompt_templates import DIAGRAM_PROMPT, TREE_PROMPT, SEQUENCE_PROMPT
from utils.logger import setup_logger

logger = setup_logger("diagram_gen")

def generate_mermaid_diagram(python_code: str, diagram_type: str = "flowchart", model_name: str = "llama-3.3-70b-versatile") -> str:
    """
    Generates a Mermaid.js diagram syntax.
    diagram_type can be 'flowchart' or 'sequence'.
    """
    if not python_code.strip():
        logger.warning("Attempted to generate Mermaid diagram from empty code.")
        return "ERROR: Cannot generate diagram from empty code."
    
    logger.info(f"Generating Mermaid {diagram_type} diagram...")
    prompt = SEQUENCE_PROMPT if diagram_type == "sequence" else DIAGRAM_PROMPT
    mermaid_syntax = call_groq_api(prompt, python_code, model_name=model_name)
    return mermaid_syntax

def render_mermaid_diagram(mermaid_code: str):
    """Renders a Mermaid.js diagram."""
    clean_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
    if "ERROR:" in mermaid_code or not clean_code:
        logger.error(f"Mermaid rendering failed: {mermaid_code}")
        st.error(f"Could not generate the architecture diagram. Details: {mermaid_code}")
    else:
        logger.info("Rendering Mermaid diagram.")
        st.subheader("Generated Diagram")
        with st.container(border=True):
            st_mermaid(clean_code, height="600px")

def generate_tree_data(python_code: str, model_name: str = "llama-3.3-70b-versatile") -> dict:
    """Generates Hierarchical JSON data for the ECharts tree."""
    if not python_code.strip():
        logger.warning("Attempted to generate tree data from empty code.")
        return {"name": "Root", "children": []}
    
    logger.info("Generating hierarchical tree data via LLM...")
    response = call_groq_api(TREE_PROMPT, python_code, model_name=model_name)
    
    try:
        data = {}
        if "---TREE_DATA---" in response:
            json_str = response.split("---TREE_DATA---")[1].strip()
            json_str = json_str.replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)
        else:
            data = json.loads(response.replace("```json", "").replace("```", "").strip())
            
        def format_nodes(node):
            label = node.get("name", "")
            sig = node.get("sig", "")
            if sig:
                node["name"] = f"{label}\n{sig}"
            if "children" in node:
                for child in node["children"]:
                    format_nodes(child)
            return node

        logger.info("Successfully parsed tree JSON data.")
        return format_nodes(data)

    except Exception as e:
        logger.error(f"Tree Data Parsing Error: {e}")
        st.error(f"Tree Data Error: {e}")
        return {"name": "Error Parsing Data", "children": []}

def render_tree_diagram(tree_data: dict):
    """Renders the Interactive Hierarchical Tree using ECharts."""
    if not tree_data:
        st.warning("No tree data available.")
        return

    option = {
        "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
        "series": [
            {
                "type": "tree",
                "data": [tree_data],
                "top": "1%",
                "left": "15%",
                "bottom": "1%",
                "right": "20%",
                "symbolSize": 12,
                "label": {
                    "position": "left",
                    "verticalAlign": "middle",
                    "align": "right",
                    "fontSize": 12,
                    "fontWeight": "bold"
                },
                "leaves": {
                    "label": {
                        "position": "right",
                        "verticalAlign": "middle",
                        "align": "left"
                    }
                },
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750
            }
        ]
    }
    
    st.subheader("Interactive Code Hierarchy")
    with st.container(border=True):
        st_echarts(options=option, height="700px")