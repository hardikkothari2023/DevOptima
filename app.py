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
from modules.prompt_templates import REFACTOR_PROMPT, OPTIMIZE_PROMPT, TRANSPILE_PROMPT, DEBUG_PROMPT, AUDIT_PROMPT, BATCH_FIX_PROMPT, SIMULATOR_PROMPT
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
        # Cyclomatic Complexity
        blocks = cc_visit(code)
        avg_cc = sum(b.complexity for b in blocks) / len(blocks) if blocks else 0
        
        # Maintainability Index
        mi_score = mi_visit(code, multi=True)
        
        # Halstead Metrics (Volume)
        h_metrics = h_visit(code)
        h_volume = h_metrics.total.volume if h_metrics else 0
        
        return {
            "complexity": avg_cc,
            "maintainability": mi_score,
            "halstead_volume": h_volume
        }
    except Exception:
        return {"complexity": 0, "maintainability": 0, "halstead_volume": 0}

def parse_custom_response(response_str: str) -> dict:
    """
    Parses the custom delimiter format from the LLM.
    Returns a dictionary with all potential keys.
    """
    data = {
        "description": "", "code": "", "warning": "", 
        "security_score": "0", "debt_grade": "F", "analysis": "", "verdict": "",
        "simulation": None
    }
    text = response_str.replace('\r\n', '\n').strip()
    
    # Parse REFRACTOR / OPTIMIZE / DEBUG format
    if "---DESCRIPTION---" in text:
        parts = text.split("---DESCRIPTION---", 1)
        if len(parts) > 1:
            content_after_desc_tag = parts[1]
            if "---CODE---" in content_after_desc_tag:
                desc, code = content_after_desc_tag.split("---CODE---", 1)
                data["description"] = desc.strip()
                data["code"] = code.strip()
                data["code"] = data["code"].replace("```python", "").replace("```", "").strip()
            else:
                data["description"] = content_after_desc_tag.strip()
    
    # Parse TRANSPILE format
    elif "---WARNING---" in text:
        parts = text.split("---WARNING---", 1)
        if len(parts) > 1:
            content_after_warn_tag = parts[1]
            if "---CODE---" in content_after_warn_tag:
                warn, code = content_after_warn_tag.split("---CODE---", 1)
                data["warning"] = warn.strip()
                data["code"] = code.strip()
                data["code"] = data["code"].replace("```python", "").replace("```", "").strip()

    # Parse AUDIT format
    elif "---SECURITY_SCORE---" in text:
        try:
            parts = text.split("---SECURITY_SCORE---")[1].split("---DEBT_GRADE---")
            data["security_score"] = parts[0].strip()
            
            parts2 = parts[1].split("---ANALYSIS---")
            data["debt_grade"] = parts2[0].strip()
            
            parts3 = parts2[1].split("---VERDICT---")
            data["analysis"] = parts3[0].strip()
            data["verdict"] = parts3[1].strip()
        except Exception:
            data["analysis"] = "Error parsing audit report."

    # Parse SIMULATOR format
    elif "---SIMULATION_DATA---" in text:
        try:
            json_str = text.split("---SIMULATION_DATA---")[1].strip()
            json_str = json_str.replace("```json", "").replace("```", "").strip()
            data["simulation"] = json.loads(json_str)
        except Exception as e:
            print(f"Simulation Parse Error: {e}")

    elif "---CODE---" in text:
        _, code = text.split("---CODE---", 1)
        data["code"] = code.strip().replace("```python", "").replace("```", "").strip()
    
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
    st.caption(f"v1.0.0 | {datetime.now().strftime('%Y-%m-%d')}")

# --- SESSION STATE INITIALIZATION ---
if 'current_code' not in st.session_state:
    st.session_state.current_code = EXAMPLE_CODE

if 'refactor_output' not in st.session_state: st.session_state.refactor_output = None
if 'optimize_output' not in st.session_state: st.session_state.optimize_output = None
if 'debug_output' not in st.session_state: st.session_state.debug_output = None
if 'transpile_output' not in st.session_state: st.session_state.transpile_output = None
if 'audit_output' not in st.session_state: st.session_state.audit_output = None
if 'fix_output' not in st.session_state: st.session_state.fix_output = None
if 'simulator_output' not in st.session_state: st.session_state.simulator_output = None

# --- UI ---
st.title("DEVOPTIMA")
st.markdown("### AI-Powered Code Transformation & Optimization")
col1, col2 = st.columns((1, 1), gap="large")

with col1:
    st.subheader(">> Code Input")
    
    if uploaded_file := st.file_uploader("Upload a Python file", type="py"):
        st.session_state.current_code = uploaded_file.getvalue().decode("utf-8")

    if (code_input := st_ace(value=st.session_state.current_code, language="python", theme="vibrant_ink", keybinding="vscode", font_size=14, height=450, wrap=True)) != st.session_state.current_code:
        st.session_state.current_code = code_input

with col2:
    st.subheader(">> AI Actions")
    tabs = st.tabs(["// AUDIT", "// SIMULATE", "// REFRACTOR", "// OPTIMIZE", "// DEBUG", "// TRANSPILE"])

    with tabs[0]: # Audit
        st.markdown("<div class=\"action-card\"><div class=\"action-card-title\">Code Quality Audit</div><div class=\"action-card-desc\">Get a comprehensive health report for your code. Analyzes security, maintainability, and complexity.</div></div>", unsafe_allow_html=True)
        
        if st.button("Generate Audit Report", key="audit", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                with st.spinner("Analyzing code metrics and security..."):
                    metrics = get_advanced_metrics(st.session_state.current_code)
                    raw_response = call_groq_api(AUDIT_PROMPT, st.session_state.current_code)
                    parsed_ai = parse_custom_response(raw_response)
                    st.session_state.audit_output = {**metrics, **parsed_ai}
                    st.session_state.fix_output = None
            else:
                st.error(f"**Validation Error:** {validation_error}")

        if st.session_state.audit_output:
            data = st.session_state.audit_output
            m1, m2, m3 = st.columns(3)
            m1.metric("Maintainability (0-100)", f"{data['maintainability']:.1f}")
            m2.metric("Cyclomatic Complexity", f"{data['complexity']:.2f}")
            m3.metric("Halstead Volume", f"{data['halstead_volume']:.0f}")

            g1, g2 = st.columns(2)
            g1.info(f"🛡️ Security Score: **{data['security_score']}/100**")
            g2.info(f"🏗️ Tech Debt Grade: **{data['debt_grade']}**")

            st.markdown("##### 🔍 Deep Analysis")
            st.warning(data["analysis"])
            st.markdown("##### 📝 Executive Verdict")
            st.success(data["verdict"])
            
            st.markdown("---")
            st.markdown("##### 🛠️ Recommended Actions")
            st.caption("Select the improvements you want to apply automatically:")
            
            c1, c2 = st.columns(2)
            fix_security = c1.checkbox("Fix Security Vulnerabilities", value=int(data.get('security_score', 100)) < 90)
            fix_style = c1.checkbox("Enforce PEP-8 & Style", value=True)
            fix_docs = c2.checkbox("Add Docstrings & Type Hints", value=True)
            fix_optimize = c2.checkbox("Optimize Logic", value=data.get('debt_grade') in ['C', 'D', 'F'])
            
            if st.button("Apply Selected Changes", key="apply_audit_fixes", use_container_width=True):
                selected_fixes = []
                if fix_security: selected_fixes.append("- Fix all security vulnerabilities found.")
                if fix_style: selected_fixes.append("- Format code according to PEP-8 standards.")
                if fix_docs: selected_fixes.append("- Add Google-style docstrings and Python type hints.")
                if fix_optimize: selected_fixes.append("- Optimize inefficient logic and reduce complexity.")
                
                if selected_fixes:
                    fix_instructions = "\n".join(selected_fixes)
                    formatted_prompt = BATCH_FIX_PROMPT.replace("{selected_fixes}", fix_instructions)
                    with st.spinner("Applying selected fixes..."):
                        raw_response = call_groq_api(formatted_prompt, st.session_state.current_code)
                        st.session_state.fix_output = parse_custom_response(raw_response)
                else:
                    st.warning("Please select at least one improvement to apply.")

            if st.session_state.fix_output:
                fix_data = st.session_state.fix_output
                st.markdown("##### ✅ Applied Changes")
                if fix_data["description"]: st.info(fix_data["description"])
                if fix_data["code"]:
                    st_code_diff(old_string=st.session_state.current_code, new_string=fix_data["code"], language='python')
                    st.download_button("Download Improved Code", fix_data["code"], "improved_code.py", "text/plain", key="dl_audit_code")

    with tabs[1]: # Simulator
        st.markdown("<div class=\"action-card\"><div class=\"action-card-title\">The Simulator: Zero-Execution Trace</div><div class=\"action-card-desc\">Visualize exactly how your code runs, step-by-step, without executing it. Use 'Chaos Mode' to test edge cases and potential crashes.</div></div>", unsafe_allow_html=True)
        
        chaos_mode = st.checkbox("🔥 Chaos Mode (Test Edge Cases / Breaks)", value=False)
        
        if st.button("Start Simulation", key="simulate", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                prompt = SIMULATOR_PROMPT
                if chaos_mode:
                    prompt = prompt.replace("SCENARIO:", "SCENARIO: CHAOS_MODE REQUESTED. Find an edge case.")
                
                with st.spinner(f"AI Core is running {'Chaos' if chaos_mode else 'Mental'} Simulation..."):
                    raw_response = call_groq_api(prompt, st.session_state.current_code)
                    st.session_state.simulator_output = parse_custom_response(raw_response)
            else:
                st.error(f"**Validation Error:** {validation_error}")
        
        if st.session_state.simulator_output and st.session_state.simulator_output.get("simulation"):
            sim_data = st.session_state.simulator_output["simulation"]
            
            st.markdown(f"**Scenario:** `{sim_data.get('scenario', 'Unknown')}`")
            st.markdown(f"**Complexity:** `{sim_data.get('complexity_note', 'N/A')}`")
            
            st.markdown("##### 🕵️ Execution Trace")
            for step in sim_data.get("trace", []):
                with st.container():
                    c1, c2, c3 = st.columns([1, 4, 3])
                    c1.markdown(f"**Step {step.get('step')}**")
                    c2.code(step.get('line'), language='python')
                    c3.caption(f"📝 {step.get('action')}")
                    c3.code(f"State: {step.get('variables')}", language='text')
                    st.divider()
            
            st.markdown("##### 🏁 Final Outcome")
            outcome = sim_data.get("outcome", "")
            if "Error" in outcome or "Exception" in outcome:
                st.error(outcome)
            else:
                st.success(outcome)

    with tabs[2]: # Refactor
        st.markdown("<div class=\"action-card\"><div class=\"action-card-title\">Intelligent Code Refactoring</div><div class=\"action-card-desc\">This AI agent analyzes your Python code and rewrites it for optimal clarity and maintainability. It adds type hints, generates docstrings, and ensures PEP-8 standards.</div></div>", unsafe_allow_html=True)
        
        if st.button("Execute Refactor", key="refactor", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                with st.spinner("AI core is refactoring sequence..."):
                    raw_response = call_groq_api(REFACTOR_PROMPT, st.session_state.current_code)
                    st.session_state.refactor_output = parse_custom_response(raw_response)
            else:
                st.error(f"**Validation Error:** {validation_error}")

        if st.session_state.refactor_output:
            data = st.session_state.refactor_output
            if data["description"]:
                st.markdown("##### AI Analysis & Metrics")
                st.info(data["description"])
            
            if data["code"]:
                refactored_code = data["code"]
                original_complexity = get_average_complexity(st.session_state.current_code)
                new_complexity = get_average_complexity(refactored_code)
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Original Avg. Complexity", f"{original_complexity:.2f}")
                m_col2.metric("New Avg. Complexity", f"{new_complexity:.2f}", delta=f"{(new_complexity - original_complexity):.2f}")
                
                st.markdown("##### Code Diff")
                st_code_diff(old_string=st.session_state.current_code, new_string=refactored_code, language='python')
                st.download_button("Download Code", refactored_code, "refactored_code.py", "text/plain", key="dl_refactor_code")
    
    with tabs[3]: # Optimize
        st.markdown("<div class=\"action-card\"><div class=\"action-card-title\">Algorithmic Performance Optimization</div><div class=\"action-card-desc\">The optimization agent identifies inefficient algorithms and replaces them with high-performance alternatives, improving execution speed.</div></div>", unsafe_allow_html=True)
        
        if st.button("Execute Optimize", key="optimize", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                with st.spinner("AI core is optimizing algorithms..."):
                    raw_response = call_groq_api(OPTIMIZE_PROMPT, st.session_state.current_code)
                    st.session_state.optimize_output = parse_custom_response(raw_response)
            else:
                st.error(f"**Validation Error:** {validation_error}")

        if st.session_state.optimize_output:
            data = st.session_state.optimize_output
            if data["description"]:
                st.markdown("##### AI Analysis & Metrics")
                st.info(data["description"])

            if data["code"]:
                optimized_code = data["code"]
                original_complexity = get_average_complexity(st.session_state.current_code)
                new_complexity = get_average_complexity(optimized_code)
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Original Avg. Complexity", f"{original_complexity:.2f}")
                m_col2.metric("New Avg. Complexity", f"{new_complexity:.2f}", delta=f"{(new_complexity - original_complexity):.2f}")

                st.markdown("##### Code Diff")
                st_code_diff(old_string=st.session_state.current_code, new_string=optimized_code, language='python')
                st.download_button("Download Code", optimized_code, "optimized_code.py", "text/plain", key="dl_optimize_code")

    with tabs[4]: # Debug
        st.markdown("<div class=\"action-card\"><div class=\"action-card-title\">Intelligent Debugging & Repair</div><div class=\"action-card-desc\">Detects logic bugs, runtime errors, and security flaws. Paste an error log for precise fixing, or let the AI scan your code automatically.</div></div>", unsafe_allow_html=True)
        
        error_log = st.text_area("Paste Error Message / Traceback (Optional)", placeholder="e.g. ZeroDivisionError: division by zero...", height=100)
        
        if st.button("Execute Debug Scan", key="debug", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                # Inject user's error log into the prompt
                formatted_prompt = DEBUG_PROMPT.replace("{error_log}", error_log if error_log else "None provided.")
                
                with st.spinner("AI core is diagnosing issues..."):
                    raw_response = call_groq_api(formatted_prompt, st.session_state.current_code)
                    st.session_state.debug_output = parse_custom_response(raw_response)
            else:
                st.error(f"**Validation Error:** {validation_error}")

        if st.session_state.debug_output:
            data = st.session_state.debug_output
            
            # Check for "NO ISSUES FOUND" signal
            if data["description"] and "NO ISSUES FOUND" in data["description"]:
                st.success("✅ Analysis Complete: No logical errors or bugs detected.")
                st.info(data["description"])
            else:
                if data["description"]:
                    st.markdown("##### Diagnosis & Fix")
                    st.warning(data["description"]) # Use warning color for bug diagnosis
                
                if data["code"]:
                    st.markdown("##### Patched Code")
                    st_code_diff(old_string=st.session_state.current_code, new_string=data["code"], language='python')
                    st.download_button("Download Fixed Code", data["code"], "fixed_code.py", "text/plain", key="dl_debug_code")
                    
    with tabs[5]: # Transpile
        st.markdown("<div class=\"action-card\"><div class=\"action-card-title\">Polyglot Code Transpilation</div><div class=\"action-card-desc\">Translate Python to other languages. The AI checks for library compatibility before translation.</div></div>", unsafe_allow_html=True)
        languages = ["Rust", "JavaScript", "Go", "C++", "Java", "TypeScript", "C#", "Swift", "Kotlin", "PHP"]
        target_lang = st.selectbox("Select Target Language", languages)
        
        if st.button(f"Execute Transpile to {target_lang}", key="transpile", use_container_width=True):
            if not (validation_error := validate_python_code(st.session_state.current_code)):
                dynamic_prompt = f"TARGET LANGUAGE: {target_lang}\n\n{TRANSPILE_PROMPT}"
                with st.spinner(f"AI core is analyzing and transpiling to {target_lang}..."):
                    raw_response = call_groq_api(dynamic_prompt, st.session_state.current_code)
                    st.session_state.transpile_output = parse_custom_response(raw_response)
            else:
                st.error(f"**Validation Error:** {validation_error}")

        if st.session_state.transpile_output:
            data = st.session_state.transpile_output
            if data["warning"]:
                st.warning(data["warning"], icon="⚠️")
            
            if data["code"]:
                st.success(f"Transpile to {target_lang} complete.")
                transpiled_code = data["code"]
                st.code(transpiled_code, language=target_lang.lower())
                st.download_button("Download Code", transpiled_code, f"transpiled_code.{target_lang.lower()}", key="dl_transpile_code")