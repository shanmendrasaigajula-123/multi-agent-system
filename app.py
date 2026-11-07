import streamlit as st
import re
import html
from datetime import date
from bs4 import BeautifulSoup

from src.pipelines.pipeline import run_research_pipeline


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="NEXUS AI | Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# DEMO USAGE LIMITS
# ==================================================

MAX_RUNS = 3        # runs allowed per visitor session
DAILY_LIMIT = 12    # runs allowed per day across ALL visitors
                    # (~10-15K tokens per run on Groq's 200K/day free budget)

if "runs" not in st.session_state:
    st.session_state["runs"] = 0


@st.cache_resource
def get_global_counter():
    # Shared across all sessions while the server is running.
    # Resets when Render restarts the app.
    return {"date": None, "count": 0}


def daily_runs_used():
    counter = get_global_counter()
    today = str(date.today())

    if counter["date"] != today:
        counter["date"] = today
        counter["count"] = 0

    return counter["count"]


def increment_daily_runs():
    counter = get_global_counter()
    counter["count"] += 1


def is_rate_limit_error(message):
    text = str(message).lower()
    return "429" in text or "rate limit" in text or "rate_limit" in text


# ==================================================
# HTML CLEANING FUNCTION
# ==================================================

def clean_content(content):

    if not content:
        return ""

    content = html.unescape(str(content))

    soup = BeautifulSoup(content, "html.parser")

    # Remove unwanted elements
    for tag in soup([
        "script",
        "style",
        "meta",
        "link",
        "iframe"
    ]):
        tag.decompose()

    cleaned = soup.get_text(separator="\n", strip=True)

    return cleaned


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0b1020;
    color: #e5e7eb;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #263247;
}

/* Hero Section */

.hero {
    padding: 38px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #172554,
        #312e81,
        #1e1b4b
    );
    border: 1px solid #3730a3;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 40px;
    font-weight: 800;
    color: white;
    margin-bottom: 10px;
}

.hero p {
    color: #c7d2fe;
    font-size: 15px;
}

/* Section Titles */

.section-title {
    font-size: 23px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 18px;
    color: #f8fafc;
}

/* Agent Cards */

.agent-card {
    background: #151e32;
    border: 1px solid #29364d;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 12px;
}

.agent-card h4 {
    color: #a5b4fc;
    margin-bottom: 8px;
}

.agent-card p {
    color: #cbd5e1;
    font-size: 13px;
}

/* Metrics */

div[data-testid="stMetric"] {
    background: #151e32;
    border: 1px solid #29364d;
    padding: 18px;
    border-radius: 12px;
}

/* Buttons */

.stButton > button {
    background: linear-gradient(
        90deg,
        #6366f1,
        #8b5cf6
    );
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    height: 48px;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #4f46e5,
        #7c3aed
    );
    color: white;
    border: none;
}

/* Input */

.stTextInput input {
    background-color: #151e32;
    color: white;
    border: 1px solid #374151;
    border-radius: 8px;
}

/* Tabs */

.stTabs [data-baseweb="tab"] {
    color: #cbd5e1;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: #818cf8 !important;
}

/* Divider */

hr {
    border-color: #29364d;
}

/* Footer */

.footer {
    text-align: center;
    color: #64748b;
    padding: 20px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("# 🔬 NEXUS AI")

    st.caption("MULTI-AGENT RESEARCH SYSTEM")

    st.markdown("---")

    st.markdown("### About the System")

    st.write(
        "An intelligent research assistant powered by "
        "multiple AI agents that collaborate to generate "
        "detailed research reports."
    )

    st.markdown("---")

    st.markdown("### AI Agents")

    st.markdown("""
    **01 — Search Agent**

    Searches the web for relevant information.

    ---

    **02 — Reader Agent**

    Scrapes webpages and extracts useful content.

    ---

    **03 — Writer Agent**

    Generates structured research reports.

    ---

    **04 — Critic Agent**

    Evaluates reports and provides feedback.
    """)

    st.markdown("---")

    st.markdown("### Technology Stack")

    st.markdown("""
    - LangChain
    - LangGraph
    - Groq LLM
    - Tavily Search
    - Python
    - Streamlit
    """)

    st.markdown("---")

    st.caption("NEXUS AI | Research Intelligence")


# ==================================================
# MAIN HEADER
# ==================================================

st.markdown("""
<div class="hero">
<h1>Research Intelligence.</h1>
<p>
Your AI-powered research workspace.
Search, analyze, synthesize and evaluate
information using autonomous AI agents.
</p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# RESEARCH INPUT
# ==================================================

st.markdown(
    '<div class="section-title">Start Your Research</div>',
    unsafe_allow_html=True
)

topic = st.text_input(
    "Research Topic",
    placeholder="Example: Impact of Generative AI on the job market in 2026"
)

col1, col2 = st.columns([1, 3])

with col1:

    research_button = st.button(
        "🚀 Generate Research",
        use_container_width=True
    )

with col2:

    remaining = max(MAX_RUNS - st.session_state["runs"], 0)

    st.caption(
        "Four AI agents will collaborate to generate your research report. "
        f"Demo runs remaining: {remaining} / {MAX_RUNS}"
    )


# ==================================================
# RUN RESEARCH PIPELINE
# ==================================================

if research_button:

    if not topic.strip():

        st.warning("Please enter a research topic.")

    elif st.session_state["runs"] >= MAX_RUNS:

        st.warning(
            f"Demo limit reached ({MAX_RUNS} runs per session). "
            "Check the GitHub repo to run it with your own API keys."
        )

    elif daily_runs_used() >= DAILY_LIMIT:

        st.warning(
            "The demo's daily quota has been used up. "
            "Please try again tomorrow."
        )

    else:

        # Remove any previous result so an old report is not shown
        # if the new research run fails.
        st.session_state.pop("research_result", None)
        st.session_state.pop("research_topic", None)

        try:

            with st.status(
                "Initializing NEXUS AI Research System...",
                expanded=True
            ) as status:

                st.write("🔍 Search Agent: Searching the web...")
                st.write("📖 Reader Agent: Extracting webpage content...")
                st.write("✍️ Writer Agent: Generating research report...")
                st.write("🧠 Critic Agent: Evaluating the report...")

                result = run_research_pipeline(topic.strip())

                # The pipeline must return a dictionary.
                if not isinstance(result, dict):
                    raise TypeError(
                        "The research pipeline did not return a valid result. "
                        "Check that run_research_pipeline() ends with 'return state'."
                    )

                # Search or report-generation failures are returned in this field.
                if result.get("error"):
                    status.update(
                        label="Research could not be completed.",
                        state="error",
                        expanded=True
                    )

                    if is_rate_limit_error(result["error"]):
                        st.error(
                            "The demo's daily AI quota is used up. "
                            "Please try again later."
                        )
                    else:
                        st.error(result["error"])

                else:
                    st.session_state["research_result"] = result
                    st.session_state["research_topic"] = topic.strip()

                    # Count only successful runs
                    st.session_state["runs"] += 1
                    increment_daily_runs()

                    status.update(
                        label="Research completed successfully!",
                        state="complete",
                        expanded=False
                    )

                    st.success("Your research report is ready!")

        except Exception as e:

            if is_rate_limit_error(e):
                st.error(
                    "The demo's daily AI quota is used up. "
                    "Please try again later."
                )
            else:
                st.error(f"Research pipeline failed: {str(e)}")


# ==================================================
# DISPLAY RESEARCH RESULTS
# ==================================================

result = st.session_state.get("research_result")

if isinstance(result, dict):

    research_topic = st.session_state.get("research_topic", "Untitled Research")

    st.markdown("---")

    st.markdown(
        '<div class="section-title">Research Dashboard</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------
    # EXTRACT CRITIC SCORE
    # --------------------------------------------------

    feedback = result.get("feedback", "")

    score_match = re.search(
        r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        str(feedback)
    )

    score = score_match.group(1) if score_match else "N/A"


    # --------------------------------------------------
    # DASHBOARD METRICS
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Research Status",
            "Completed"
        )

    with col2:

        st.metric(
            "AI Agents",
            "4",
            "Pipeline"
        )

    with col3:

        st.metric(
            "Critic Score",
            f"{score}/10"
        )


    st.markdown("---")


    # ==================================================
    # RESULT TABS
    # ==================================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Research Report",
        "🔍 Search Results",
        "📖 Scraped Content",
        "🧠 Critic Review"
    ])


    # ==================================================
    # TAB 1: RESEARCH REPORT
    # ==================================================

    with tab1:

        st.markdown("### Final Research Report")

        st.caption(f"Topic: {research_topic}")

        report = result.get("report", "")

        if report:

            st.markdown(report)

            st.download_button(
                label="⬇️ Download Research Report",
                data=report,
                file_name="NEXUS_AI_Research_Report.md",
                mime="text/markdown"
            )

        else:

            st.warning("No research report generated.")


    # ==================================================
    # TAB 2: SEARCH RESULTS
    # ==================================================

    with tab2:

        st.markdown("### Web Search Results")

        search_results = result.get("search_results", "")

        if search_results:

            st.text_area(
                "Search Output",
                value=str(search_results),
                height=450
            )

        else:
            st.warning("No search results available.")


    # ==================================================
    # TAB 3: SCRAPED CONTENT
    # ==================================================

    with tab3:

        st.markdown("### Extracted Webpage Content")

        scraped_content = result.get("scraped_content", "")

        if scraped_content:

            st.text_area(
                "Scraped Webpage Content",
                value=str(scraped_content),
                height=500
            )

        else:
            st.warning("No scraped content available.")

    # ==================================================
    # TAB 4: CRITIC REVIEW
    # ==================================================

    with tab4:

        st.markdown("### Research Evaluation")

        st.metric(
            "Overall Research Score",
            f"{score}/10"
        )

        st.markdown("---")

        if feedback and str(feedback).strip():

            st.markdown(feedback)

        elif result.get("critic_error"):

            st.error(
                f"Critic Agent failed: {result['critic_error']}"
            )

        else:

            st.warning("The Critic Agent returned an empty response.")


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.markdown("""
<div class="footer">
<b>NEXUS AI</b> · Multi-Agent Research Assistant
<br><br>
Built with Streamlit, LangChain, LangGraph and Groq.
</div>
""", unsafe_allow_html=True)