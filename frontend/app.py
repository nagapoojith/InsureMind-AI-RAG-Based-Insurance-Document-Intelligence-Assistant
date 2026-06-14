import base64
import html
import os
import sys
import time
import streamlit as st

# ================= PATH SETUP =================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from backend.rag_engine import ask_question

# ================= CONFIG =================
frontend_dir = os.path.dirname(os.path.abspath(__file__))
SIDEBAR_LOGO_IMAGE = os.path.join(frontend_dir, "logo.png")
TITLE_IMAGE = os.path.join(frontend_dir, "title logo.png")
USER_IMAGE = os.path.join(frontend_dir, "user image.png")
BOT_IMAGE = os.path.join(frontend_dir, "chatbot image.jpg")
workspace_dir = os.path.dirname(project_root)
DATA_FOLDER = os.path.join(workspace_dir, "INSURANCE DATA")

st.set_page_config(
    page_title="InsureMind",
    page_icon=TITLE_IMAGE,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================= SESSION =================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "show_docs" not in st.session_state:
    st.session_state.show_docs = False


# ================= HELPERS =================
def clear_chat():
    st.session_state.chat_history = []
    st.session_state.latest_result = None


def toggle_docs():
    st.session_state.show_docs = not st.session_state.show_docs


def get_docs():
    docs = []
    if os.path.exists(DATA_FOLDER):
        for f in os.listdir(DATA_FOLDER):
            if f.lower().endswith(".pdf"):
                docs.append(f)
    return sorted(docs)


def image_to_base64(path):
    if not os.path.exists(path):
        return ""

    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()


def safe_html(value):
    return html.escape(str(value)).replace("\n", "<br>")


sidebar_logo_img = image_to_base64(SIDEBAR_LOGO_IMAGE)
title_img = image_to_base64(TITLE_IMAGE)
user_img = image_to_base64(USER_IMAGE)
bot_img = image_to_base64(BOT_IMAGE)

# ================= CSS =================
st.markdown("""
<style>
:root {
    --bg-start: #edf2ff;
    --bg-end: #f8fbff;
    --vpad: 24px; /* vertical padding for top & bottom (reduced) */
    --panel-deep: #231942;
    --panel-mid: #2f2a7f;
    --panel-soft: rgba(255, 255, 255, 0.12);
    --card: rgba(255, 255, 255, 0.82);
    --card-border: rgba(255, 255, 255, 0.45);
    --accent: #4338ca;
    --accent-2: #7c3aed;
    --text: #111827;
    --muted: #5b6472;
}

/* Force whole-page layout containment to eliminate page-level scrolling */
html, body, [data-testid="stAppViewContainer"], .stApp {
    height: 100vh !important;
    min-height: 100vh !important;
    max-height: 100vh !important;
    width: 100vw !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(124, 58, 237, 0.10), transparent 30%),
        radial-gradient(circle at top right, rgba(67, 56, 202, 0.10), transparent 28%),
        linear-gradient(135deg, var(--bg-start), var(--bg-end));
    color: var(--text);
    font-family: "Segoe UI Variable", "Segoe UI", "Aptos", sans-serif;
}

/* Ensure there is visible padding at the very top and bottom of the app */
.stApp {
    padding-top: var(--vpad) !important;
    padding-bottom: var(--vpad) !important;
}

/* Remove all possible unwanted top spaces in Streamlit */
header, [data-testid="stHeader"] {
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    display: none !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stAppViewBlockContainer"],
section.main,
div.block-container,
.main .block-container {
    padding-top: 0px !important;
    margin-top: 0px !important;
}

[data-testid="stMain"] > div:first-child {
    padding-top: 0px !important;
}

[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
}

[data-testid="stDecoration"] {
    display: none;
}

[data-testid="stStatusWidget"] {
    display: none;
}

[data-testid="stSidebar"] {
    display: none;
}

/* Tighten main content padding to start close to top */
section.main > div.block-container {
    padding: var(--vpad) 16px var(--vpad) 16px !important; /* symmetric top & bottom padding */
    max-width: 100% !important;
    height: calc(100% - (var(--vpad) * 2)) !important;
    min-height: calc(100% - (var(--vpad) * 2)) !important;
    max-height: calc(100% - (var(--vpad) * 2)) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Columns visual alignment & equal height block */
div[data-testid="stHorizontalBlock"] {
    height: calc(100vh - 22px) !important;
    min-height: calc(100vh - 22px) !important;
    max-height: calc(100vh - 22px) !important;
    gap: 12px !important;
    align-items: stretch !important;
    display: flex !important;
    flex-direction: row !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Make each st.column transparent and span 100% height */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

/* Remove Streamlit's default top padding from all inner column wrappers */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    margin: 0 !important;
    background: transparent !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div > div {
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
}

/* Ensure column wrappers containing stVerticalBlockBorderWrapper or stContainer expand fully */
div[data-testid="element-container"]:has([data-testid="stVerticalBlockBorderWrapper"]),
div[data-testid="element-container"]:has([data-testid="stContainer"]) {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    height: auto !important;
    display: flex !important;
    flex-direction: column !important;
}

/* LEFT SIDEBAR FIXED & GRADIENT OVERLAY height correction */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) [data-testid="stVerticalBlockBorderWrapper"] {
    flex: 0 0 auto !important;
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    overflow: hidden !important;
    background: linear-gradient(180deg, #22194c 0%, #312e81 55%, #2f2a7f 100%) !important;
    border-radius: 24px !important;
    padding: 16px 12px !important;
    box-shadow: 0 18px 44px rgba(17, 24, 39, 0.20) !important;
    box-sizing: border-box !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    position: relative !important;
    isolation: isolate !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) [data-testid="stVerticalBlockBorderWrapper"] > div {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
    flex: 1 1 auto !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
}

div[data-testid="stHorizontalBlock"] > div:first-child,
div[data-testid="stHorizontalBlock"] > div:nth-child(1),
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1),
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div > div {
    background: linear-gradient(180deg, #22194c 0%, #312e81 55%, #2f2a7f 100%);
    border-radius: 24px;
    padding: 16px 12px;
    height: 100% !important; /* Locked exactly to column's full bottom line! */
    min-height: 100% !important;
    max-height: 100% !important;
    box-shadow: 0 18px 44px rgba(17, 24, 39, 0.20);
    box-sizing: border-box;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px;
    position: relative;
    isolation: isolate;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child *,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) * {
    box-sizing: border-box;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div > div {
    color: white;
}

.left-panel-inner {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 100%;
    max-height: 100%;
    width: 100%;
    overflow: hidden;
    gap: 8px;
}

.left-panel-top {
    flex: 0 0 auto;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.left-panel-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 0 0 auto;
    width: 100%;
}

.left-panel-scroll {
    flex: 1 1 auto;
    overflow-y: auto !important;
    overflow-x: hidden;
    padding-right: 4px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 8px 0;
}

.logo {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    object-fit: cover;
    display: block;
    margin: auto;
    border: 3px solid rgba(255,255,255,0.22);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15);
}

.logo-title {
    text-align: center;
    font-size: 22px;
    font-weight: 800;
    color: white;
    margin-top: 5px;
    letter-spacing: 0.2px;
}

.logo-sub {
    text-align: center;
    color: rgba(255, 255, 255, 0.92);
    margin-bottom: 6px;
    font-size: 12px;
}

.panel-divider {
    height: 1px;
    background: rgba(255,255,255,0.16);
    margin: 4px 0 0;
}

/* Beautiful nested internal scrolling list of documents */
.doc-scroll {
    max-height: calc(100vh - 430px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding-right: 4px;
    margin-bottom: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
}

.doc-item {
    background: rgba(255,255,255,0.10);
    padding: 8px 10px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.14);
    color: white;
    font-size: 13px;
    line-height: 1.35;
    overflow-wrap: anywhere;
    word-break: break-word;
    flex-shrink: 0;
}

.status-card {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 18px;
    padding: 12px;
    color: white;
    margin-top: auto;
    box-sizing: border-box;
    overflow: hidden;
    flex-shrink: 0;
    font-size: 12px;
    width: 100%;
}

.metric {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 4px 0;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.96);
    line-height: 1.2;
}

.metric-icon {
    width: 18px;
    flex: 0 0 18px;
    text-align: center;
    line-height: 1;
    font-size: 14px;
}

/* CENTER PANEL - HERO & CHAT CONTAINER */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) > div > div {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important; /* Full height column */
    min-height: 100% !important;
    max-height: 100% !important;
    gap: 12px !important;
    overflow: hidden !important;
}

.hero {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 24px;
    padding: 12px 16px;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    text-align: center;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04), inset 0 1px 0 rgba(255,255,255,0.6);
    border: 1px solid rgba(255, 255, 255, 0.5);
    flex: 0 0 auto !important;
    box-sizing: border-box;
    height: 130px !important; /* Strictly constant header height */
    min-height: 130px !important;
    max-height: 130px !important;
}

.hero-img {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    object-fit: cover;
    display: block;
    margin: auto;
    box-shadow: 0 12px 28px rgba(67, 56, 202, 0.16);
}

.hero-title {
    font-size: 22px;
    font-weight: 800;
    color: #1e1b4b;
    margin-top: 4px;
    line-height: 1.15;
}

.hero-sub {
    font-size: 12px;
    color: var(--muted);
}

/* Outer Chat Box Frame (Styling matches perfectly and dynamically ends at exact bottom visual coordinate) */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] {
    flex: 0 0 auto !important;
    height: calc(100% - 142px) !important; /* Locked exactly to column's bottom (100% minus 130px Hero and 12px Gap) */
    min-height: calc(100% - 142px) !important;
    max-height: calc(100% - 142px) !important;
    overflow: hidden !important;
    background: rgba(255, 255, 255, 0.82) !important; /* Visible Frosted Glass White card! */
    border: 1px solid rgba(99, 102, 241, 0.22) !important; /* Sleek outline border */
    border-radius: 28px !important;
    padding: 16px !important;
    box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08) !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    box-sizing: border-box !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] > div {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
    flex: 1 1 auto !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Inner Messages Container inside the Blue Box (transparent and scrollable) */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
    height: calc(100% - 74px) !important; /* Leaves exactly 74px for bottom chat input and padding */
    min-height: calc(100% - 74px) !important;
    max-height: calc(100% - 74px) !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    overflow-y: auto !important;
    margin: 0 0 8px 0 !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] > div {
    height: auto !important;
    display: block !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
    height: auto !important;
    overflow-y: visible !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    padding-right: 4px !important;
}

/* Card messages styling with robust bottom margin spacing */
.card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 22px;
    padding: 16px 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    margin-bottom: 12px !important; /* Added solid 12px space between the chatting cards */
    box-sizing: border-box;
    overflow-wrap: anywhere;
    word-wrap: break-word;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.bot-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 12px;
    flex-shrink: 0;
    border: 2px solid rgba(255, 255, 255, 0.6);
}

.user-title {
    font-weight: 800;
    font-size: 17px;
    color: #111827;
}

.bot-title {
    font-weight: 800;
    font-size: 17px;
    color: var(--accent);
}

.msg {
    margin-top: 10px;
    line-height: 1.75;
    color: #1f2937;
    overflow-wrap: anywhere;
    word-break: break-word;
    white-space: normal;
}

.msg img {
    max-width: 100%;
}

/* Chat input parent wrapper and chat input layout perfectly locked INSIDE the frosted glass container */
[data-testid="stChatInputContainer"],
div[data-testid="stChatInput"] {
    position: relative !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 6px 0 0 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    z-index: 99 !important;
    flex: 0 0 auto !important;
    box-sizing: border-box !important;
}

div[data-testid="stChatInput"] textarea {
    border-radius: 14px !important;
}

/* RIGHT PANEL & SCROLLING */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) > div > div {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important; /* Full height column */
    min-height: 100% !important;
    max-height: 100% !important;
    overflow: hidden !important;
}

/* Style the stContainer wrapper inside the third column to stretch perfectly to the bottom */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) [data-testid="stVerticalBlockBorderWrapper"] {
    flex: 0 0 auto !important;
    height: 100% !important; /* Locked exactly to column's full bottom line! */
    min-height: 100% !important;
    max-height: 100% !important;
    overflow: hidden !important;
    background: rgba(255, 255, 255, 0.82) !important;
    border: 1px solid rgba(255, 255, 255, 0.45) !important;
    border-radius: 24px !important;
    padding: 16px !important;
    box-shadow: 0 18px 44px rgba(17, 24, 39, 0.08) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-sizing: border-box !important;
    margin: 0 !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) [data-testid="stVerticalBlockBorderWrapper"] > div {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
    flex: 1 1 auto !important;
    overflow-y: auto !important;
    padding-right: 4px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
}

.answer-card {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    margin-bottom: 12px;
    color: #111827;
    box-sizing: border-box;
}

.answer-title {
    font-size: 16px;
    font-weight: 800;
    color: var(--accent);
    margin-bottom: 12px;
}

.source-box {
    padding: 12px 14px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.62);
    border: 1px solid rgba(148, 163, 184, 0.20);
    margin-bottom: 10px;
    line-height: 1.6;
    color: #111827;
    overflow-wrap: anywhere;
    word-break: break-word;
}

.excerpt-box {
    padding: 14px 14px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.62);
    border: 1px solid rgba(148, 163, 184, 0.20);
    margin-bottom: 10px;
    line-height: 1.7;
    color: #111827;
    overflow-wrap: anywhere;
    word-break: break-word;
    white-space: normal;
}

.empty-state {
    background: rgba(255, 255, 255, 0.60);
    border: 1px dashed rgba(99, 102, 241, 0.18);
    border-radius: 18px;
    padding: 18px 16px;
    color: var(--muted);
    text-align: center;
    line-height: 1.6;
    margin-top: 6px;
    width: 100%;
}

.status-live {
    background: rgba(238, 242, 255, 0.92);
    border: 1px solid #c7d2fe;
    padding: 14px 16px;
    border-radius: 18px;
    margin-bottom: 15px;
    font-weight: 600;
    color: #312e81;
    box-sizing: border-box;
}

/* Native buttons styling */
div.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 40px;
    background: rgba(17, 24, 39, 0.96);
    color: white;
    border: none;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 0;
    padding: 8px 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.14);
    transition: transform 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
    flex-shrink: 0;
}

div.stButton > button:hover {
    background: rgba(31, 41, 55, 0.98);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.20);
}

div.stButton {
    width: 100%;
    margin: 0;
    flex-shrink: 0;
}

/* Beautiful Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 99px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.5);
}

/* Screen responsive adjustments */
@media (max-width: 1200px) {
    section.main > div.block-container {
        padding: 8px 12px !important;
    }

    .hero-title {
        font-size: 22px;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 8px !important;
    }
}

/* Make Streamlit file uploader visible and styled for dark left panel */
.stFileUploader, .stFileUploader * {
    color: white !important;
}
.stFileUploader > div {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 8px !important;
    box-shadow: none !important;
}
.stFileUploader button, .stFileUploader [role="button"] {
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
input[type="file"] {
    color: white !important;
}

/* Give extra top padding to left panel inner content so items align visually */
.left-panel-inner {
    padding-top: 12px !important;
}
/* Strong override: ensure top/bottom padding is visible and not clipped */
[data-testid="stAppViewContainer"], [data-testid="stMain"], section.main, div.block-container, .stApp {
    height: auto !important;
    min-height: 100% !important;
    overflow: visible !important;
    padding-top: var(--vpad) !important;
    padding-bottom: var(--vpad) !important;
}

/* Make sure horizontal block respects the available height inside the padded container */
div[data-testid="stHorizontalBlock"] {
    height: auto !important;
    min-height: calc(100% - (var(--vpad) * 2)) !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LAYOUT =================
PANEL_HEIGHT = 600
MESSAGE_AREA_HEIGHT = 360

left, center, right = st.columns([0.95, 2.5, 1.1], gap="small")

# ================= LEFT PANEL =================
with left:
    left_panel = st.container(height=PANEL_HEIGHT, border=True)

    with left_panel:
        st.markdown('<div class="left-panel-inner">', unsafe_allow_html=True)
        st.markdown('<div class="left-panel-top">', unsafe_allow_html=True)

        if sidebar_logo_img:
            st.markdown(f'<img src="data:image/png;base64,{sidebar_logo_img}" class="logo">', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="logo-title">InsureMind</div>
            <div class="logo-sub">AI Insurance Assistant</div>
            <div class="panel-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="left-panel-actions">', unsafe_allow_html=True)

        if st.button("💬 New Chat"):
            clear_chat()
            st.rerun()

        if st.button("📂 Documents"):
            toggle_docs()
            st.rerun()

        # File uploader for PDFs
        uploaded_files = st.file_uploader("📤 Upload PDFs", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            os.makedirs(DATA_FOLDER, exist_ok=True)
            saved = []
            for up in uploaded_files:
                save_path = os.path.join(DATA_FOLDER, up.name)
                with open(save_path, "wb") as f:
                    f.write(up.getbuffer())
                saved.append(up.name)
            st.success(f"Saved {len(saved)} file(s) to {DATA_FOLDER}")
            # show docs list after upload
            st.session_state.show_docs = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="left-panel-scroll">', unsafe_allow_html=True)

        if st.session_state.show_docs:
            docs = get_docs()
            if docs:
                doc_items_html = "".join([f'<div class="doc-item">{safe_html(doc)}</div>' for doc in docs])
            else:
                doc_items_html = '<div class="doc-item">No PDFs found</div>'
            st.markdown(f'<div class="doc-scroll">{doc_items_html}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="status-card">
                <h3 style="color:white;margin:0 0 6px;font-size:13px;font-weight:700;">System Status</h3>
                <div class="metric"><span class="metric-icon">🟢</span><span>All Systems Online</span></div>
                <div class="metric"><span class="metric-icon">🤖</span><span>llama3.2:3b</span></div>
                <div class="metric"><span class="metric-icon">🧠</span><span>BGE Embeddings</span></div>
                <div class="metric"><span class="metric-icon">🎯</span><span>MiniLM Reranker</span></div>
                <div class="metric"><span class="metric-icon">🗄️</span><span>ChromaDB</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)

# ================= CENTER PANEL =================
with center:
    st.markdown(
        f"""
        <div class="hero">
            <img src="data:image/png;base64,{sidebar_logo_img}" class="hero-img">
            <div class="hero-title">Hi! I'm InsureMind AI</div>
            <div class="hero-sub">Ask about your insurance policies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Beautiful single outer container (Creates the frosted glass box enclosing both chat and input)
    # Give it a height parameter so Streamlit ALWAYS instantiates data-testid="stVerticalBlockBorderWrapper"
    chat_card = st.container(height=PANEL_HEIGHT, border=True)

    with chat_card:
        # Inner scrollable chat container for the messages
        # Give it a height parameter to ensure it is wrapped in stVerticalBlockBorderWrapper
        chat_container = st.container(height=MESSAGE_AREA_HEIGHT, border=False)

        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    user_avatar = f'<img src="data:image/png;base64,{user_img}" class="bot-avatar">' if user_img else ""
                    st.markdown(
                        f"""<div class="card">
<div style="display:flex;align-items:center;gap:10px;min-width:0;">
{user_avatar}
<div class="user-title">You</div>
</div>
<div class="msg">{safe_html(msg["content"])}</div>
</div>""",
                        unsafe_allow_html=True,
                    )
                else:
                    bot_avatar = f'<img src="data:image/jpeg;base64,{bot_img}" class="bot-avatar">' if bot_img else ""
                    st.markdown(
                        f"""<div class="card">
<div style="display:flex;align-items:center;gap:10px;min-width:0;">
{bot_avatar}
<div class="bot-title">InsureMind AI</div>
</div>
<div class="msg">{safe_html(msg["content"])}</div>
</div>""",
                        unsafe_allow_html=True,
                    )

        # The chat input sits perfectly nested inside the outer frosted glass box
        query = st.chat_input("Ask the question...")

    if query:
        st.session_state.chat_history.append({
            "role": "user",
            "content": query
        })

        progress_box = st.empty()

        progress_box.markdown(
            '<div class="status-live">🔍 Searching policy documents...</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.4)

        progress_box.markdown(
            '<div class="status-live">📌 Ranking best evidence...</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.4)

        progress_box.markdown(
            '<div class="status-live">📝 Generating response...</div>',
            unsafe_allow_html=True
        )

        result = ask_question(query)

        progress_box.empty()

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"]
        })

        st.session_state.latest_result = result
        st.rerun()

# ================= RIGHT PANEL =================
with right:
    # Give it a height parameter to ensure it generates stVerticalBlockBorderWrapper
    right_container = st.container(height=PANEL_HEIGHT, border=True)

    with right_container:
        if st.session_state.latest_result:
            result = st.session_state.latest_result

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-title">📌 ANSWER</div>
                    <div class="msg">{safe_html(result["answer"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if result["found"]:
                st.markdown(
                    '<div class="answer-card"><div class="answer-title">📄 SOURCES</div></div>',
                    unsafe_allow_html=True,
                )

                for src in result["sources"]:
                    st.markdown(
                        f"""
                        <div class="source-box">
                            <strong>{safe_html(src["document"])}</strong><br>
                            Page {safe_html(src["page"])}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    '<div class="answer-card"><div class="answer-title">🧾 EXCERPT</div></div>',
                    unsafe_allow_html=True,
                )

                for excerpt in result["excerpts"]:
                    st.markdown(
                        f"""
                        <div class="excerpt-box">
                            {safe_html(excerpt)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div class="empty-state">Ask a question to see answers here</div>',
                unsafe_allow_html=True
            )