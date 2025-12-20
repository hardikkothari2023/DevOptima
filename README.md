# 🚀 DEVOPTIMA

### The Intelligent Code Modernization Platform

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-ff69b4.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live App](https://img.shields.io/badge/Live_App-Online-brightgreen.svg)](https://devoptima-by-hardik.streamlit.app/)

> DevOptima is not just a tool; it's an AI-powered command center designed to analyze, modernize, and perfect Python code. It transforms the developer from a coder into an architect by providing a suite of intelligent directives, wrapped in a premium, "Cyber-Minimalist" UI.

---

## ✨ Live Demo

Experience the platform live. No installation required.

### **[➡️ Launch DevOptima](https://devoptima-by-hardik.streamlit.app/)**

---

## Core Features: The AI Directives

DevOptima's power is divided into six distinct, color-coded AI tools, each serving a unique purpose in the software development lifecycle.

| Icon | Feature | Purpose |
| :--- | :--- | :--- |
| 🛡️ | **AUDIT** | Get a comprehensive "Health Check" of your code before making changes. |
| 🔮 | **SIMULATE** | Visualize code execution step-by-step without actually running it. |
| 🛠️ | **REFACTOR** | Automatically improve code clarity, style, and maintainability. |
| 🚀 | **OPTIMIZE** | Reduce code execution time by improving algorithmic efficiency. |
| 🐞 | **DEBUG** | Find and fix bugs automatically, with or without an error log. |
| 🌐 | **TRANSPILE** | Translate Python code into other popular programming languages. |

---

## 🗺️ Future Vision: The Roadmap

DevOptima is architected for evolution. Here are the world-class features on our immediate roadmap, designed to push the boundaries of AI-assisted development.

### 1. 🤖 **The Autonomous Agent: Self-Healing Code**
**The Vision:** To transform the AI from a "suggester" into an autonomous engineer. Instead of just *proposing* a fix, the AI will write, test, and validate its own code in a loop until it's proven to work.

**How it works:**
1.  **Hypothesis (AI Writes):** The AI generates a code fix.
2.  **Experiment (Sandbox Execution):** The system safely compiles the code with `ast.parse()` to check for syntax errors. If it passes, it's run in a restricted `exec()` environment to catch runtime errors.
3.  **Result & Refine:**
    *   **Success?** The verified code is presented to the user.
    *   **Failure?** The error message is captured and fed back into a `SELF_CORRECTION_PROMPT`. The AI is told, "Your last attempt failed with this error. Try again."
4.  **Loop:** This "Hypothesize -> Test -> Refine" cycle repeats up to 3 times, ensuring the final output is syntactically and logically sound.

### 2. ⚡ **The Live Canvas: A True IDE in the Browser**
**The Vision:** To replace the static text box with the same high-performance Monaco editor that powers VS Code, creating a seamless, "live" coding experience.

**How it works:**
1.  **Library Upgrade:** We will replace `streamlit-ace` with `streamlit-monaco` to enable advanced IDE features.
2.  **"Ghost Text" Autocomplete:**
    *   As you type, the editor will send partial code snippets to a fast LLM endpoint.
    *   The AI's prediction for the rest of the line will appear as gray "ghost text," which can be accepted with a single `Tab`.
3.  **Interactive Data Visualization:**
    *   Leveraging the Monaco Hover Provider API, hovering over a variable during a **Simulation** will trigger a popup chart showing its value history throughout the execution trace.

---

## 🛠️ Technology Stack & Architecture

DevOptima uses a modern, Python-based stack to deliver a seamless and powerful user experience.

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | Streamlit | For building the entire interactive UI with Python. |
| **AI Core** | Groq API | Provides high-speed access to a Large Language Model for all AI tasks. |
| **Code Metrics** | Radon | A Python library used in the Audit feature for calculating code complexity. |
| **Code Editor** | `streamlit-ace` | Provides the embedded, high-quality code editor. |
| **Code Diff Viewer**| `streamlit-code-diff` | Renders the "before-and-after" code comparisons. |
| **Styling** | Custom CSS | Injected to create the premium, modern "Cyber-Minimalist" user interface. |
| **Prompt Engineering**| Custom Delimiters | A robust, custom-built parsing system (`---TAG---`) is used instead of JSON to ensure reliable communication with the AI. |

---

## 🚀 Getting Started (Local Development)

To run DevOptima on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/devoptima.git
    cd devoptima
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment:**
    - Create a `.env` file and add your Groq API key:
      ```
      GROQ_API_KEY="your_api_key_here"
      ```

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```