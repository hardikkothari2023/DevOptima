"""
Main Streamlit application file for DevOptima.
This is the final, stable version with all features and bug fixes.
"""
import shutil
import json
import streamlit as st
from streamlit_ace import st_ace
from datetime import datetime
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
from streamlit_code_diff import st_code_diff

# Import local modules
from modules.llm_handler import call_groq_api
from modules.prompt_templates import REFACTOR_PROMPT, OPTIMIZE_PROMPT, TRANSPILE_PROMPT, DEBUG_PROMPT, AUDIT_PROMPT, BATCH_FIX_PROMPT, SIMULATOR_PROMPT, HINGLISH_PROMPT, PYTHON_TO_HINGLISH_PROMPT
from modules.diagram_gen import generate_mermaid_diagram, render_mermaid_diagram, generate_tree_data, render_tree_diagram
from modules.code_parser import validate_python_code
from utils.example_code import EXAMPLE_CODE
from utils.style import get_css

# --- HELPER FUNCTIONS ---
def get_system_info() -> str:
    """Checks for GPU availability via nvidia-smi."""
    if shutil.which("nvidia-smi"):
        return "⚡ GPU Detected"
    return "💻 CPU Mode"

def get_average_complexity(code: str) -> float:
    """Calculates the average cyclomatic complexity of a code block."""
    try:
        blocks = cc_visit(code)
        if not blocks: return 0.0
        return sum(b.complexity for b in blocks) / len(blocks)
    except Exception:
        return 0.0

def get_advanced_metrics(code: str) -> dict:
    """Calculates advanced metrics using Radon."""
    try:
        blocks = cc_visit(code)
        avg_cc = sum(b.complexity for b in blocks) / len(blocks) if blocks else 0
        mi_score = mi_visit(code, multi=True)
        h_metrics = h_visit(code)
        h_volume = h_metrics.total.volume if h_metrics else 0
        return {"complexity": avg_cc, "maintainability": mi_score, "halstead_volume": h_volume}
    except Exception:
        return {"complexity": 0, "maintainability": 0, "halstead_volume": 0}

def parse_custom_response(response_str: str) -> dict:
    """Parses the custom delimiter format from the LLM."""
    data = {"description": "", "code": "", "warning": "", "security_score": "0", "debt_grade": "F", "analysis": "", "verdict": "", "simulation": None}
    text = response_str.replace('\r\n', '\n').strip()
    if "---DESCRIPTION---" in text:
        parts = text.split("---DESCRIPTION---", 1)
        if len(parts) > 1:
            content = parts[1]
            if "---CODE---" in content:
                desc, code = content.split("---CODE---", 1)
                data["description"], data["code"] = desc.strip(), code.strip().replace("```python", "").replace("```", "").strip()
            else: data["description"] = content.strip()
    elif "---WARNING---" in text:
        parts = text.split("---WARNING---", 1)
        if len(parts) > 1:
            content = parts[1]
            if "---CODE---" in content:
                warn, code = content.split("---CODE---", 1)
                data["warning"], data["code"] = warn.strip(), code.strip().replace("```python", "").replace("```", "").strip()
    elif "---SECURITY_SCORE---" in text:
        try:
            parts = text.split("---SECURITY_SCORE---")[1].split("---DEBT_GRADE---")
            data["security_score"] = parts[0].strip()
            parts2 = parts[1].split("---ANALYSIS---")
            data["debt_grade"] = parts2[0].strip()
            parts3 = parts2[1].split("---VERDICT---")
            data["analysis"], data["verdict"] = parts3[0].strip(), parts3[1].strip()
        except Exception: data["analysis"] = "Error parsing audit report."
    elif "---SIMULATION_DATA---" in text:
        try:
            json_str = text.split("---SIMULATION_DATA---")[1].strip().replace("```json", "").replace("```", "").strip()
            data["simulation"] = json.loads(json_str)
        except Exception: pass
    elif "---CODE---" in text:
        data["code"] = text.split("---CODE---", 1)[1].strip().replace("```python", "").replace("```", "").strip()
    elif "def " in text or "import " in text:
        data["code"] = text.replace("```python", "").replace("```", "").strip()
    return data

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DevOptima", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")
st.markdown(get_css(), unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("DevOptima")
    st.markdown("---")
    st.info(get_system_info())
    st.caption(f"v2.0.0 | {datetime.now().strftime('%Y-%m-%d')}")

# --- SESSION STATE ---
if 'current_code' not in st.session_state: st.session_state.current_code = EXAMPLE_CODE
for key in ['refactor_output', 'optimize_output', 'debug_output', 'transpile_output', 'audit_output', 'fix_output', 'simulator_output', 'hinglish_output']:
    if key not in st.session_state: st.session_state[key] = None

# --- UI HEADER ---
st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">DEVOPTIMA</h1>
        <div class="hero-subtitle">The Intelligent Code Modernization Platform</div>
        <div>
            <span class="hero-badge badge-version">v2.0.0 Pro</span>
            <span class="hero-badge badge-status">● System Online</span>
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns((1, 1), gap="large")

with col1:
    st.markdown("### 💻 Code Workspace")
    if uploaded_file := st.file_uploader("Upload Python Source", type="py"):
        st.session_state.current_code = uploaded_file.getvalue().decode("utf-8")
    st.session_state.current_code = st_ace(value=st.session_state.current_code, language="python", theme="vibrant_ink", keybinding="vscode", font_size=14, height=500, wrap=True)

with col2:
    st.markdown("### ⚡ AI Directives")
    tabs = st.tabs(["🛡️ AUDIT", "🔮 SIMULATE", "🛠️ REFACTOR", "🚀 OPTIMIZE", "🐞 DEBUG", "🌐 TRANSPILE", "🗺️ VISUALIZE", "🧠 HINGLISH"])

    with tabs[0]: # Audit
        st.markdown('<div class="action-card card-audit"><div class="action-card-title">🛡️ Code Quality Audit</div><div class="action-card-desc">Deep-scan architecture for security risks, maintainability issues, and technical debt. Generates a comprehensive engineering verdict.</div></div>', unsafe_allow_html=True)
        if st.button("Generate Audit Report", key="audit", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                with st.spinner("Executing deep scan..."):
                    metrics = get_advanced_metrics(st.session_state.current_code)
                    parsed_ai = parse_custom_response(call_groq_api(AUDIT_PROMPT, st.session_state.current_code))
                    st.session_state.audit_output = {"complexity": metrics["complexity"], "maintainability": metrics["maintainability"], "halstead_volume": metrics["halstead_volume"], **parsed_ai}
                    st.session_state.fix_output = None
            else: st.error(err)
        if st.session_state.audit_output:
            data = st.session_state.audit_output
            m1, m2, m3 = st.columns(3)
            m1.metric("Maintainability", f"{data['maintainability']:.1f}")
            m2.metric("Complexity", f"{data['complexity']:.2f}")
            m3.metric("Halstead Vol.", f"{data['halstead_volume']:.0f}")
            st.info(f"🛡️ Security: **{data['security_score']}/100** | 🏗️ Debt Grade: **{data['debt_grade']}**")
            st.warning(data["analysis"])
            st.success(data["verdict"])
            st.markdown("---")
            c1, c2 = st.columns(2)
            f_sec, f_sty = c1.checkbox("Fix Security", int(data.get('security_score', 100)) < 90), c1.checkbox("Fix Style", True)
            f_doc, f_opt = c2.checkbox("Add Docs", True), c2.checkbox("Optimize", data.get('debt_grade') in ['C', 'D', 'F'])
            if st.button("Apply Selected Changes", key="apply_audit", use_container_width=True):
                fixes = []
                if f_sec: fixes.append("- Fix security.")
                if f_sty: fixes.append("- PEP-8 style.")
                if f_doc: fixes.append("- Add docstrings/types.")
                if f_opt: fixes.append("- Optimize logic.")
                if fixes:
                    with st.spinner("Applying fixes..."):
                        st.session_state.fix_output = parse_custom_response(call_groq_api(BATCH_FIX_PROMPT.replace("{selected_fixes}", "\n".join(fixes)), st.session_state.current_code))
            if st.session_state.fix_output:
                st.info(st.session_state.fix_output["description"])
                st_code_diff(old_string=st.session_state.current_code, new_string=st.session_state.fix_output["code"], language='python')

    with tabs[1]: # Simulate
        st.markdown('<div class="action-card card-simulate"><div class="action-card-title">🔮 Logic Simulation</div><div class="action-card-desc">Execute code in a virtual environment to visualize data flow and state changes without side effects. High-fidelity mental trace.</div></div>', unsafe_allow_html=True)
        chaos = st.checkbox("🔥 Chaos Mode (Test Edge Cases)", False)
        if st.button("Run Simulation", key="sim", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                prompt = SIMULATOR_PROMPT.replace("SCENARIO:", "SCENARIO: CHAOS_MODE. Find edge cases.") if chaos else SIMULATOR_PROMPT
                with st.spinner("Simulating execution..."):
                    st.session_state.simulator_output = parse_custom_response(call_groq_api(prompt, st.session_state.current_code))
            else: st.error(err)
        if st.session_state.simulator_output and st.session_state.simulator_output.get("simulation"):
            sim = st.session_state.simulator_output["simulation"]
            st.caption(f"Scenario: {sim.get('scenario')} | {sim.get('complexity_note')}")
            for s in sim.get("trace", []):
                with st.container():
                    c1, c2 = st.columns([1, 4])
                    c1.markdown(f"**Step {s.get('step')}**")
                    c2.code(s.get('line'), language='python')
                    st.caption(f"Action: {s.get('action')} | State: {s.get('variables')}")
                    st.divider()
            st.success(sim.get("outcome"))

    with tabs[2]: # Refactor
        st.markdown('<div class="action-card card-refactor"><div class="action-card-title">🛠️ Code Refactoring</div><div class="action-card-desc">Modernize code for PEP-8 compliance. Inject type hints, Google-style docstrings, and improve modularity.</div></div>', unsafe_allow_html=True)
        if st.button("Execute Refactor", key="refactor", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                with st.spinner("Refactoring..."):
                    st.session_state.refactor_output = parse_custom_response(call_groq_api(REFACTOR_PROMPT, st.session_state.current_code))
            else: st.error(err)
        if st.session_state.refactor_output:
            st.info(st.session_state.refactor_output["description"])
            st_code_diff(old_string=st.session_state.current_code, new_string=st.session_state.refactor_output["code"], language='python')

    with tabs[3]: # Optimize
        st.markdown('<div class="action-card card-optimize"><div class="action-card-title">🚀 Performance Optimization</div><div class="action-card-desc">Identify algorithmic bottlenecks. Replace inefficient loops with high-performance vectorization or better Big-O alternatives.</div></div>', unsafe_allow_html=True)
        if st.button("Execute Optimize", key="optimize", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                with st.spinner("Optimizing..."):
                    st.session_state.optimize_output = parse_custom_response(call_groq_api(OPTIMIZE_PROMPT, st.session_state.current_code))
            else: st.error(err)
        if st.session_state.optimize_output:
            st.info(st.session_state.optimize_output["description"])
            st_code_diff(old_string=st.session_state.current_code, new_string=st.session_state.optimize_output["code"], language='python')

    with tabs[4]: # Debug
        st.markdown('<div class="action-card card-debug"><div class="action-card-title">🐞 Intelligent Debugger</div><div class="action-card-desc">Heal broken code instantly. Paste an error log or let the AI scan for hidden logic bugs and security leaks.</div></div>', unsafe_allow_html=True)
        log = st.text_area("Paste Error/Traceback", height=100)
        if st.button("Run Debug Scan", key="debug", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                with st.spinner("Diagnosing..."):
                    st.session_state.debug_output = parse_custom_response(call_groq_api(DEBUG_PROMPT.replace("{error_log}", log if log else "None"), st.session_state.current_code))
            else: st.error(err)
        if st.session_state.debug_output:
            st.warning(st.session_state.debug_output["description"])
            if st.session_state.debug_output["code"]:
                st_code_diff(old_string=st.session_state.current_code, new_string=st.session_state.debug_output["code"], language='python')

    with tabs[5]: # Transpile
        st.markdown('<div class="action-card card-transpile"><div class="action-card-title">🌐 Code Transpilation</div><div class="action-card-desc">Seamlessly translate Python to production languages like Rust, Go, or TypeScript while maintaining logic parity.</div></div>', unsafe_allow_html=True)
        lang = st.selectbox("Target Language", ["Rust", "JavaScript", "Go", "C++", "Java", "TypeScript", "Swift", "Kotlin"])
        if st.button(f"Transpile to {lang}", key="trans", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                with st.spinner("Transpiling..."):
                    st.session_state.transpile_output = parse_custom_response(call_groq_api(f"TARGET LANGUAGE: {lang}\n\n{TRANSPILE_PROMPT}", st.session_state.current_code))
            else: st.error(err)
        if st.session_state.transpile_output:
            if st.session_state.transpile_output["warning"]: st.warning(st.session_state.transpile_output["warning"])
            st.code(st.session_state.transpile_output["code"], language=lang.lower())

    with tabs[6]: # Visualize
        st.markdown('<div class="action-card card-simulate"><div class="action-card-title">🗺️ Architecture Visualization</div><div class="action-card-desc">Generate instant flowcharts, sequence diagrams, and interactive class maps from your code.</div></div>', unsafe_allow_html=True)
        
        viz_type = st.radio("Select View:", ["Flowchart", "Sequence Diagram", "Interactive Code Map"], horizontal=True)
        
        if st.button("Generate Visualization", key="gen_viz", use_container_width=True):
            if not (err := validate_python_code(st.session_state.current_code)):
                with st.spinner("Analyzing architecture..."):
                    if viz_type == "Interactive Code Map":
                        tree_data = generate_tree_data(st.session_state.current_code)
                        render_tree_diagram(tree_data)
                    else:
                        d_type = "sequence" if viz_type == "Sequence Diagram" else "flowchart"
                        mermaid_code = generate_mermaid_diagram(st.session_state.current_code, d_type)
                        render_mermaid_diagram(mermaid_code)
            else: st.error(err)

    with tabs[7]: # Hinglish
        st.markdown('<div class="action-card card-transpile"><div class="action-card-title">🧠 Desi Logic Studio</div><div class="action-card-desc">The ultimate bridge between Hinglish and Python. Choose your mode below.</div></div>', unsafe_allow_html=True)
        
        mode = st.radio("Select Mode:", ["Hinglish ⮕ Python", "Python ⮕ Hinglish"], horizontal=True)
        
        if mode == "Hinglish ⮕ Python":
            st.info("💡 Write logic in Hinglish (e.g., 'bol bhai') and convert it to real Python code.")
            hinglish_input = st.text_area("Enter Hinglish Logic:", height=200, placeholder="Example:\nbhai ye hai a = 0\njab tak bhai (a < 10)\n  bol bhai a\n  a = a + 1", key="h_input")
            if st.button("Generate Python Code", key="hinglish_gen", use_container_width=True):
                if hinglish_input.strip():
                    with st.spinner("Translating Desi Logic..."):
                        st.session_state.hinglish_output = parse_custom_response(call_groq_api(HINGLISH_PROMPT, hinglish_input))
                else:
                    st.warning("Please enter some Hinglish logic first!")
            
            if st.session_state.hinglish_output and mode == "Hinglish ⮕ Python":
                if st.session_state.hinglish_output.get("code"):
                    st.markdown("### 🐍 Generated Python")
                    err = validate_python_code(st.session_state.hinglish_output["code"])
                    if err:
                        st.error(f"Generated code has errors: {err}")
                    st.code(st.session_state.hinglish_output["code"], language="python")
                    st.download_button(
                        label="Download Python Code",
                        data=st.session_state.hinglish_output["code"],
                        file_name="desi_logic.py",
                        mime="text/x-python",
                        use_container_width=True
                    )
        
        else: # Python ⮕ Hinglish
            st.info("💡 Convert the Python code in your Workspace into funny and educational Hinglish logic.")
            if st.button("Explain Workspace in Hinglish", key="python_to_h", use_container_width=True):
                with st.spinner("Decoding to Desi style..."):
                    st.session_state.hinglish_output = parse_custom_response(call_groq_api(PYTHON_TO_HINGLISH_PROMPT, st.session_state.current_code))
            
            if st.session_state.hinglish_output and mode == "Python ⮕ Hinglish":
                if st.session_state.hinglish_output.get("description"):
                    st.success(st.session_state.hinglish_output["description"])
                if st.session_state.hinglish_output.get("code"):
                    st.markdown("### 🧠 Desi Translation")
                    st.markdown(f'<div class="desi-box">{st.session_state.hinglish_output["code"]}</div>', unsafe_allow_html=True)
