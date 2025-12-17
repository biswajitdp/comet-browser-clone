import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# CONFIG
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = "https://api.tavily.com/search"

st.set_page_config(
    page_title="Asteroid Browser",
    page_icon="🪐",
    layout="centered"
)
# FUNCTION
def tavily_search(query, max_results=5):
    """Safe Tavily search that NEVER crashes Streamlit"""
    if not TAVILY_API_KEY:
        st.error("❌ TAVILY_API_KEY is missing")
        return None

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query.strip(),
        "include_answer": True,
        "include_images": True,
        "include_raw_content": False,
        "max_results": max_results
    }

    try:
        response = requests.post(TAVILY_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        # ✅ SAFE normalization
        answer = data.get("answer")

        if isinstance(answer, str):
            data["answer"] = answer.strip()
        else:
            data["answer"] = ""

        # Ensure results is always a list
        if not isinstance(data.get("results"), list):
            data["results"] = []

        # Ensure images is always a list
        if not isinstance(data.get("images"), list):
            data["images"] = []

        return data

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Tavily API Error: {e}")
        return None

# THEME TOGGLE (TOP, NOT SIDEBAR)
if "dark" not in st.session_state:
    st.session_state.dark = True

col1, col2 = st.columns([7, 1])
with col2:
    st.session_state.dark = st.toggle("🌗", value=st.session_state.dark, help="Toggle Dark Mode")

DARK = st.session_state.dark


# CUSTOM CSS
st.markdown(f"""
<style>
  :root {{
    --bg: {'#0b0f17' if DARK else '#ffffff'};
    --text: {'#e5e7eb' if DARK else '#0f172a'};
    --muted: {'#94a3b8' if DARK else '#475569'};
    --card-bg: {'#121826' if DARK else '#ffffff'};
    --card-fg: {'#e5e7eb' if DARK else '#0f172a'};
    --card-border: {'#334155' if DARK else '#e2e8f0'};
    --accent: #e63946;
    --link: #60a5fa;
    --shadow: 0 4px 12px rgba(0,0,0,{0.35 if DARK else 0.08});
  }}

  .main {{
    background: var(--bg);
    color: var(--text);
  }}

  h1, h2, h3, h4, h5, label, p, span {{
    color: var(--text) !important;
    font-family: "Segoe UI", sans-serif !important;
  }}

  .stTabs [aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom: 3px solid var(--accent) !important;
  }}

  .answer-box {{
    background: var(--card-bg);
    color: var(--card-fg);
    border-radius: 12px;
    padding: 22px 25px;
    line-height: 1.6;
    font-size: 16.5px;
    box-shadow: var(--shadow);
    border-top: 4px solid var(--accent);
    margin-top: 20px;
    margin-bottom: 25px;
  }}

  .answer-box:hover {{
    transform: translateY(-2px);
    transition: all 0.2s ease;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
  }}

  .source-time {{
    color: var(--muted);
    font-size: 13px;
  }}

  .source-title a {{
    color: var(--link);
    text-decoration: none;
  }}

  .source-title a:hover {{
    text-decoration: underline;
  }}

  .img-caption {{
    color: var(--muted);
    font-size: 13px;
    text-align: center;
  }}

  .source-link {{
    text-decoration: none;
    font-size: 14px;
    color: var(--link);
  }}

  hr {{
    border: none;
    height: 1px;
    background: var(--card-border);
    margin: 1rem 0;
  }}

  .header {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
  }}
</style>
""", unsafe_allow_html=True)


# HEADER
st.markdown(
    """
    <div class="header">
        <h1 style="font-size:48px;">🪐 Asteroid</h1>
    </div>
    <p style="text-align:center; color:gray; margin-top:-10px;">A Comet Browser Clone...</p>
    <hr>
    """,
    unsafe_allow_html=True
)

# SEARCH INPUT
st.markdown("### 🔍 Search")
query = st.text_input("Enter your query...", placeholder="Type your question here and press Enter")
search_btn = st.button("Search")

if search_btn and query:
    with st.spinner("🔎 Searching Tavily..."):
        data = tavily_search(query)
else:
    data = None


# RESULTS SECTION
tab1, tab2, tab3 = st.tabs(["Results", "Sources", "Images"])

# ====== TAB 1: RESULTS ======
with tab1:
    if not data:
        st.info("Search for something to see the answer here.")
    else:
        answer_text = data.get("answer")
        if not answer_text and data.get("results"):
            answer_text = data["results"][0].get("content", "")

        if answer_text:
            st.markdown(
                f"""
                <div class="answer-box">
                    <strong>🧠 Answer:</strong><br>{answer_text}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("No consistent answer found for this query.")


# ====== TAB 2: SOURCES ======
with tab2:
    if not data or "results" not in data:
        st.info("No sources yet. Start a search first.")
    else:
        st.markdown("## 🌐 Sources")
        for item in data["results"]:
            title = item.get("title", "Untitled")
            url = item.get("url", "#")
            content = item.get("content", "")
            published_date = item.get("published_date", "")
            if published_date:
                try:
                    date_obj = datetime.strptime(published_date, "%a, %d %b %Y %H:%M:%S %Z")
                    published_date = date_obj.strftime("%a, %d %b %Y %I:%M:%S %p %Z")
                except:
                    pass

            st.markdown(f"**[{title}]({url})**")
            if published_date:
                st.markdown(f"<span class='source-time'>{published_date}</span>", unsafe_allow_html=True)
            if content:
                st.write(content[:350] + "...")
            st.markdown("---")


# ====== TAB 3: IMAGES ======
with tab3:
    if not data or not data.get("images"):
        st.info("No images found for this query.")
    else:
        st.markdown("## 🖼️ Related Images")
        images = data.get("images", [])
        cols = st.columns(3)
        for i, img in enumerate(images):
            col = cols[i % 3]
            with col:
                if isinstance(img, str):
                    st.image(img, use_container_width=True)
                elif isinstance(img, dict):
                    st.image(img.get("url"), use_container_width=True)
                    if img.get("source_url"):
                        st.markdown(
                            f"<a href='{img['source_url']}' target='_blank'>🔗 Source Link</a>",
                            unsafe_allow_html=True
                        )
                    if img.get("caption"):
                        st.markdown(f"<div class='img-caption'>{img['caption']}</div>", unsafe_allow_html=True)
