"""
Main Streamlit application file for DevOptima.
This is the final, stable version with all features and bug fixes.
"""
import json
import streamlit as st
from streamlit_ace import st_ace
from streamlit_session_browser_storage import SessionStorage
from datetime import datetime
from radon.complexity import cc_visit
from streamlit_code_diff import st_code_diff

# Import local modules
from modules.llm_handler import call_groq_api
from modules.prompt_templates import REFACTOR_PROMPT, OPTIMIZE_PROMPT, TRANSPILE_PROMPT
from modules.code_parser import validate_python_code
from modules.diagram_gen import generate_mermaid_diagram, render_mermaid_diagram
from utils.example_code import EXAMPLE_CODE
from utils.style import get_css

# --- HELPER FUNCTIONS ---
def get_average_complexity(code: str) -> float:
    """Calculates the average cyclomatic complexity of a code block."""
    try:
        blocks = cc_visit(code)
        if not blocks: return 0.0
        return sum(b.complexity for b in blocks) / len(blocks)
    except Exception:
        return 0.0

def clean_json_response(response_str: str) -> str:
    """Cleans the AI's response by removing markdown fences."""
    return response_str.strip().replace("```json", "").replace("```", "").strip()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DevOptima", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")
st.markdown(get_css(), unsafe_allow_html=True)

# --- SESSION STATE & STORAGE ---
storage = SessionStorage()
history = storage.getItem("history") or []

if 'current_code' not in st.session_state:
    st.session_state.current_code = EXAMPLE_CODE

def add_to_history(code):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not history or history[-1]['code'] != code:
        history.append({"timestamp": timestamp, "code": code})
        if len(history) > 10: history.pop(0)
        storage.setItem("history", history)

# --- UI ---
st.title("DEVOPTIMA")
st.markdown("### AI-Powered Code Transformation & Architecture Overview")
col1, col2 = st.columns((1, 1), gap="large")

with col1:
    st.subheader(">> Code Input")
    with st.expander("🕰️ View & Load From History"):
        if not history: st.caption("Your recent code snippets will appear here.")
        else:
            for i, item in enumerate(reversed(history)):
                first_line = item['code'].split('\n')[0]
                button_label = f"{item['timestamp']} - `{first_line[:60].strip()}...`"
                if st.button(button_label, key=f"hist_{i}", use_container_width=True):
                    st.session_state.current_code = item['code']
                    st.rerun()
    
    if uploaded_file := st.file_uploader("Upload a Python file", type="py"):
        st.session_state.current_code = uploaded_file.getvalue().decode("utf-8")

    if (code_input := st_ace(value=st.session_state.current_code, language="python", theme="vibrant_ink", keybinding="vscode", font_size=14, height=450, wrap=True)) != st.session_state.current_code:
        st.session_state.current_code = code_input

with col2:
    st.subheader(">> AI Directives")
    tabs = st.tabs(["// REFRACTOR", "// OPTIMIZE", "// TRANSPILE", "// VISUALIZE"])

    with tabs[0]: # Refactor
        st.markdown("""<div class="action-card"><div class="action-card-title">Intelligent Code Refactoring</div><div class="action-card-desc">This AI agent analyzes your Python code and rewrites it for optimal clarity and maintainability. It adds type hints, generates docstrings, and ensures PEP-8 standards.</div></div>""", unsafe_allow_html=True)
        if st.button("Execute Refactor", key="refactor", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                add_to_history(st.session_state.current_code)
                with st.spinner("AI core is refactoring sequence..."):
                    response_str = call_groq_api(REFACTOR_PROMPT, st.session_state.current_code)
                
                st.success("Refactor sequence complete.")
                try:
                    cleaned_str = clean_json_response(response_str)
                    response_json = json.loads(cleaned_str)
                    description, refactored_code = response_json.get("description", ""), response_json.get("code", "")
                    
                    st.markdown("##### AI Analysis & Metrics")
                    st.info(description)
                    st.download_button("Export Analysis", description, "analysis-refactor.md", "text/markdown", key="dl_refactor_desc")
                    
                    original_complexity, new_complexity = get_average_complexity(st.session_state.current_code), get_average_complexity(refactored_code)
                    m_col1, m_col2 = st.columns(2)
                    m_col1.metric("Original Avg. Complexity", f"{original_complexity:.2f}")
                    m_col2.metric("New Avg. Complexity", f"{new_complexity:.2f}", delta=f"{(new_complexity - original_complexity):.2f}")
                    
                    st.markdown("##### Code Diff")
                    st_code_diff(old_string=st.session_state.current_code, new_string=refactored_code, language='python')
                    st.download_button("Download Code", refactored_code, "refactored_code.py", "text/plain", key="dl_refactor_code")
                except json.JSONDecodeError:
                    st.warning("Could not parse structured AI response. Showing raw output.")
                    st.code(response_str, language='text')
            else:
                st.error(f"**Validation Error:** {validation_error}")
    
    with tabs[1]: # Optimize
        st.markdown("""<div class="action-card"><div class="action-card-title">Algorithmic Performance Optimization</div><div class="action-card-desc">The optimization agent identifies inefficient algorithms and replaces them with high-performance alternatives, improving execution speed.</div></div>""", unsafe_allow_html=True)
        if st.button("Execute Optimize", key="optimize", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                add_to_history(st.session_state.current_code)
                with st.spinner("AI core is optimizing algorithms..."):
                    response_str = call_groq_api(OPTIMIZE_PROMPT, st.session_state.current_code)

                st.success("Optimization sequence complete.")
                try:
                    cleaned_str = clean_json_response(response_str)
                    response_json = json.loads(cleaned_str)
                    description, optimized_code = response_json.get("description", ""), response_json.get("code", "")

                    st.markdown("##### AI Analysis & Metrics")
                    st.info(description)
                    st.download_button("Export Analysis", description, "analysis-optimize.md", "text/markdown", key="dl_optimize_desc")

                    original_complexity, new_complexity = get_average_complexity(st.session_state.current_code), get_average_complexity(optimized_code)
                    m_col1, m_col2 = st.columns(2)
                    m_col1.metric("Original Avg. Complexity", f"{original_complexity:.2f}")
                    m_col2.metric("New Avg. Complexity", f"{new_complexity:.2f}", delta=f"{(new_complexity - original_complexity):.2f}")

                    st.markdown("##### Code Diff")
                    st_code_diff(old_string=st.session_state.current_code, new_string=optimized_code, language='python')
                    st.download_button("Download Code", optimized_code, "optimized_code.py", "text/plain", key="dl_optimize_code")
                except json.JSONDecodeError:
                    st.warning("Could not parse structured AI response. Showing raw output.")
                    st.code(response_str, language='text')
            else:
                st.error(f"**Validation Error:** {validation_error}")
                    
    with tabs[2]: # Transpile
        st.markdown("""<div class="action-card"><div class="action-card-title">Polyglot Code Transpilation</div><div class="action-card-desc">Translate Python to other languages. The robust AI checks for library compatibility before translation.</div></div>""", unsafe_allow_html=True)
        languages = ["Rust", "JavaScript", "Go", "C++", "Java", "TypeScript", "C#", "Swift", "Kotlin", "PHP"]
        target_lang = st.selectbox("Select Target Language", languages)
        if st.button(f"Execute Transpile to {target_lang}", key="transpile", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                add_to_history(st.session_state.current_code)
                dynamic_prompt = f"TARGET LANGUAGE: {target_lang}\n\n{TRANSPILE_PROMPT}"
                with st.spinner(f"AI core is analyzing and transpiling to {target_lang}..."):
                    response_str = call_groq_api(dynamic_prompt, st.session_state.current_code)

                try:
                    cleaned_str = clean_json_response(response_str)
                    response_json = json.loads(cleaned_str)
                    if "warning" in response_json:
                        st.warning(response_json["warning"], icon="⚠️")
                    elif "code" in response_json:
                        st.success(f"Transpile to {target_lang} complete.")
                        transpiled_code = response_json["code"]
                        st.code(transpiled_code, language=target_lang.lower())
                        st.download_button("Download Code", transpiled_code, f"transpiled_code.{target_lang.lower()}", key="dl_transpile_code")
                except json.JSONDecodeError:
                    st.warning("Could not parse structured AI response. Showing raw output.")
                    st.code(response_str, language='text')
            else:
                st.error(f"**Validation Error:** {validation_error}")

    with tabs[3]: # Visualize
        st.markdown("""<div class="action-card"><div class="action-card-title">Architecture Visualization</div><div class="action-card-desc">Generate a Mermaid.js flowchart to provide a clear high-level overview of the architecture.</div></div>""", unsafe_allow_html=True)
        if st.button("Execute Visualize", key="visualize", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                add_to_history(st.session_state.current_code)
                with st.spinner("AI core is visualizing architecture..."):
                    mermaid_code = generate_mermaid_diagram(st.session_state.current_code)
                st.success("Visualization complete.")
                render_mermaid_diagram(mermaid_code)
                if "ERROR" not in mermaid_code:
                    st.markdown("##### Diagram Code")
                    st.code(mermaid_code, language="markdown")
                    st.download_button("Export Mermaid Code", mermaid_code, "diagram.mmd", key="dl_mermaid")
            else:
                st.error(f"**Validation Error:** {validation_error}")
