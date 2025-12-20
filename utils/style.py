"""
Central repository for all UI/UX styling.
Uses custom CSS to override Streamlit's default look with a premium 'Cyber-Minimalist' theme.
"""

def get_css() -> str:
    return """
    <style>
        /* --- GLOBAL FONTS --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #E0E0E0;
        }
        
        /* --- BACKGROUND --- */
        .stApp {
            background-color: #0E1117;
            background-image: radial-gradient(circle at 50% 0%, #111827 0%, #0E1117 80%);
        }

        /* --- HERO SECTION ANIMATIONS --- */
        @keyframes gradient-flow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes float-up {
            0% { transform: translateY(10px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        .hero-container {
            text-align: center;
            padding: 4rem 2rem;
            margin-bottom: 3rem;
            background: radial-gradient(circle at center, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 0 40px rgba(0,0,0,0.2);
            animation: float-up 1s ease-out;
        }

        .hero-title {
            font-family: 'Inter', sans-serif;
            font-size: 5rem !important;
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 1.1;
            margin: 0;
            
            /* Animated Gradient */
            background: linear-gradient(to right, #818CF8, #C084FC, #F472B6, #818CF8);
            background-size: 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-flow 6s linear infinite;
            
            /* Glow */
            filter: drop-shadow(0 0 20px rgba(129, 140, 248, 0.4));
        }

        .hero-subtitle {
            font-size: 1.25rem;
            color: #9CA3AF;
            font-weight: 500;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        }

        .hero-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0 5px;
            backdrop-filter: blur(4px);
        }
        
        .badge-version {
            background: rgba(99, 102, 241, 0.15);
            color: #A5B4FC;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .badge-status {
            background: rgba(52, 211, 153, 0.15);
            color: #6EE7B7;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }

        /* --- CARDS & UI ELEMENTS --- */
        div[data-testid="stMetric"], div[data-testid="stExpander"], .action-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        div[data-testid="stMetric"]:hover, .action-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(129, 140, 248, 0.5);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        }

        .action-card { position: relative; overflow: hidden; margin-bottom: 2rem; }
        .action-card::before { content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%; }
        
        .action-card-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 10px; }
        .action-card-desc { font-size: 0.95rem; color: #A1A1AA; line-height: 1.6; }

        /* Specific Colors */
        .card-audit::before { background: #818CF8; } .card-audit .action-card-title { color: #818CF8; }
        .card-simulate::before { background: #22D3EE; } .card-simulate .action-card-title { color: #22D3EE; }
        .card-refactor::before { background: #A78BFA; } .card-refactor .action-card-title { color: #A78BFA; }
        .card-optimize::before { background: #34D399; } .card-optimize .action-card-title { color: #34D399; }
        .card-debug::before { background: #FBBF24; } .card-debug .action-card-title { color: #FBBF24; }
        .card-transpile::before { background: #60A5FA; } .card-transpile .action-card-title { color: #60A5FA; }

        /* --- BUTTONS --- */
        div.stButton > button {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
            color: #FFFFFF;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            font-weight: 700;
            letter-spacing: 0.05em;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        div.stButton > button:hover {
            background: #4F46E5;
            border-color: #4F46E5;
            box-shadow: 0 0 25px rgba(79, 70, 229, 0.5);
            transform: scale(1.02);
        }

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(0,0,0,0.3);
            padding: 8px;
            border-radius: 16px;
        }
        .stTabs [data-baseweb="tab"] { color: #9CA3AF; padding: 10px 16px; border-radius: 10px; }
        .stTabs [aria-selected="true"] { background-color: #4F46E5 !important; color: white !important; font-weight: 700; }
        
        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] { background-color: #05080F; }
        
        /* --- CODE --- */
        code { font-family: 'JetBrains Mono', monospace !important; }
    </style>
    """