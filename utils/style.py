"""
Contains the CSS for the final, polished dark theme.
This version introduces gradients and refined styles for a premium,
"attractive" feel as per user feedback.
"""

def get_css() -> str:
    return """
<style>
/* --- FONT --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Source+Code+Pro:wght@400;600&display=swap');

/* --- ROOT & APP --- */
:root {
    --app-bg: #0E1117;
    --primary-text: #FAFAFA;
    --secondary-text: #808191;
    --accent-color: #3B82F6;
    --accent-color-hover: #2563EB;
    --container-bg: #11141E;
    --border-color: #2D303E;
    --gradient-start: #3B82F6;
    --gradient-end: #8B5CF6;
}

.stApp {
    background-color: var(--app-bg);
    background-image: radial-gradient(circle at top left, #181A2A, var(--app-bg) 30%);
    color: var(--primary-text);
    font-family: 'Inter', sans-serif;
}

h1, h2, .st-subheader {
    font-weight: 700;
    color: var(--primary-text);
}
h3 {
    color: var(--secondary-text);
    font-weight: 400;
}

/* --- LAYOUT & CONTAINERS --- */
[data-testid="stHeader"] {
    background-color: transparent;
    border-bottom: 1px solid var(--border-color);
}
.st-emotion-cache-z5fcl4 > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
}


/* --- TABS --- */
.stTabs [data-baseweb="tab-list"] {
	gap: 8px;
    border-bottom: 2px solid var(--border-color);
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: var(--secondary-text);
    background-color: transparent;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s ease-in-out;
}
.stTabs [aria-selected="true"] {
    color: var(--accent-color);
    border-bottom: 2px solid var(--accent-color);
}
.stTabs [data-basewab="tab"]:hover {
    color: var(--accent-color);
    background-color: #1C1E2D;
}

/* --- ACTION CARD --- */
.action-card {
    background-color: rgba(28, 30, 45, 0.5);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
    transition: all 0.2s ease-in-out;
}
.action-card:hover {
    border-color: var(--accent-color);
}
.action-card-title {
    font-weight: 600;
    font-size: 1.1rem;
    color: var(--primary-text);
}
.action-card-desc {
    font-size: 0.9rem;
    color: var(--secondary-text);
    margin-bottom: 1rem;
}


/* --- BUTTONS --- */
.stButton>button {
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 1rem;
    border: none;
    background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
    color: white;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.2);
}
.stButton>button:hover {
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3);
    transform: translateY(-2px);
}
.stButton>button:active {
    transform: translateY(0);
}

/* --- CODE EDITOR & BLOCKS --- */
.ace_editor {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background-color: var(--container-bg);
}
div[data-testid="stCodeBlock"] {
    border-radius: 8px;
    border: 1px solid var(--border-color);
    background-color: #1A1A26;
}

/* --- FILE UPLOADER --- */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border-color);
    background-color: var(--container-bg);
    border-radius: 8px;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-color);
}

/* --- INFO/WARNING BOXES --- */
[data-testid="stInfo"], [data-testid="stWarning"] {
    background-color: transparent;
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent-color);
    border-radius: 8px;
}
[data-testid="stWarning"] {
    border-left-color: #FFC107;
}

/* --- MERMAID DIAGRAM TWEAKS --- */
/* Hide the default toolbar (zoom, pan buttons) from the mermaid component */
[data-testid="stMermaid"] > div[style*="position: relative;"] > div[style*="position: absolute;"] {
    display: none !important;
}

</style>
"""
