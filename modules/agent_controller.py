"""
Handles autonomous self-correction loops for AI code generation.
This module acts as a 'Controller' layer, coordinating between the LLM (Generator)
and the Code Parser (Validator).
"""

import streamlit as st
from modules.llm_handler import call_groq_api
from modules.code_parser import validate_python_code
from modules.prompt_templates import SELF_CORRECTION_PROMPT

MAX_ATTEMPTS = 3

def parse_code_from_response(response_str: str) -> str:
    """Extracts code from the LLM response format."""
    code = ""
    if "---CODE---" in response_str:
        code = response_str.split("---CODE---", 1)[1].strip()
    elif "```python" in response_str:
        code = response_str.split("```python")[1].split("```")[0].strip()
    elif "def " in response_str or "import " in response_str:
        code = response_str.strip()
    else:
        code = response_str.strip()
    
    return code.replace("```python", "").replace("```", "").strip()

def autonomous_fix_loop(initial_prompt: str, user_code: str, usage_description: str = "generating code", model_name: str = "llama-3.3-70b-versatile") -> str:
    """
    Executes a self-healing loop:
    1. Generates code via LLM.
    2. Validates syntax.
    3. If invalid, feeds error back to LLM for correction.
    4. Repeats up to MAX_ATTEMPTS.
    
    Returns:
        The raw LLM response string (success) or the last failed response.
    """
    
    current_prompt = initial_prompt
    last_response = ""
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        # 1. Generate (or Regenerate)
        if attempt > 1:
            st.toast(f"⚠️ Attempt {attempt}/{MAX_ATTEMPTS}: Self-correcting syntax error...", icon="🔄")
        
        response = call_groq_api(current_prompt, user_code, model_name=model_name)
        last_response = response
        
        # 2. Extract Code for Validation
        # Note: We need to parse the custom format to get just the code for the validator
        generated_code = parse_code_from_response(response)
        
        # 3. Validate
        error_msg = validate_python_code(generated_code)
        
        if not error_msg:
            # SUCCESS: Code is valid
            if attempt > 1:
                st.toast("✅ Self-correction successful!", icon="✨")
            return response
            
        # FAILURE: Prepare for next iteration
        print(f"Validation failed on attempt {attempt}: {error_msg}")
        
        # Update prompt for next loop
        current_prompt = SELF_CORRECTION_PROMPT.replace(
            "{previous_code}", generated_code
        ).replace(
            "{error_message}", error_msg
        )
        
        # The 'user_code' for the correction prompt is actually irrelevant 
        # because the prompt embeds the 'previous_code', but we keep the signature valid.
        user_code = "" 

    st.error(f"❌ Autonomous Agent failed to generate valid code after {MAX_ATTEMPTS} attempts.")
    return last_response
