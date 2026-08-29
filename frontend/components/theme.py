"""
Visual identity for the CASD frontend: dark gray + vibrant yellow.

`.streamlit/config.toml` sets the base Streamlit theme; this module adds
a bit of extra CSS on top for cards, badges and nicer buttons/metrics.
"""

import streamlit as st

COLORS = {
    "bg": "#1B1B1D",
    "bg_secondary": "#242426",
    "card": "#2A2A2D",
    "border": "#3A3A3D",
    "yellow": "#FFD60A",
    "yellow_soft": "#FFE566",
    "text": "#F5F5F5",
    "text_muted": "#9A9A9E",
    "success": "#4CAF50",
    "danger": "#FF5C5C",
}


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLORS['bg']};
        }}
        [data-testid="stSidebar"] {{
            background-color: {COLORS['bg_secondary']};
            border-right: 1px solid {COLORS['border']};
        }}
        h1, h2, h3 {{
            color: {COLORS['text']} !important;
        }}
        h1 {{
            border-bottom: 3px solid {COLORS['yellow']};
            padding-bottom: .4rem;
            display: inline-block;
        }}
        .stButton > button,
        .stFormSubmitButton > button {{
            background-color: {COLORS['yellow']};
            color: #1B1B1D;
            font-weight: 700;
            border: none;
            border-radius: 8px;
            padding: .5rem 1.2rem;
            transition: background-color .15s ease-in-out;
        }}
        .stButton > button:hover,
        .stFormSubmitButton > button:hover {{
            background-color: {COLORS['yellow_soft']};
            color: #1B1B1D;
        }}
        .stButton > button:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_muted']};
        }}
        [data-testid="stMetric"] {{
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1rem;
        }}
        [data-testid="stMetricValue"] {{
            color: {COLORS['yellow']};
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        }}
        .casd-card {{
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: .8rem;
        }}
        .casd-card-icon {{ font-size: 1.6rem; }}
        .casd-card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {COLORS['text']};
            margin: .2rem 0 .3rem 0;
        }}
        .casd-card-desc {{
            color: {COLORS['text_muted']};
            font-size: .88rem;
            min-height: 2.6rem;
        }}
        .casd-badge {{
            display: inline-block;
            padding: .15rem .6rem;
            border-radius: 999px;
            font-size: .78rem;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
