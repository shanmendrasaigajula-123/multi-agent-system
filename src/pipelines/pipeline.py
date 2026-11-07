
from langchain_core.messages import ToolMessage
import re
from src.tools.tools import scrape_url

from src.agents.agents import (
    build_search_agent,
    writer_chain,
    critic_chain,   # replaces critic_prompt and llm
)


def run_research_pipeline(topic: str) -> dict:

    state = {
        "topic": topic,
        "search_results": "",
        "scraped_content": "",
        "report": "",
        "feedback": ""
    }

    # ==========================================
    # STEP 1 - SEARCH AGENT
    # ==========================================

    print("\n" + "=" * 50)
    print("Step 1 - Search Agent is working...")
    print("=" * 50)

    try:
        search_agent = build_search_agent()

        search_result = search_agent.invoke({
            "messages": [
                ("user", f"Find recent, reliable and detailed information about: {topic}")
            ]
        })

        state["search_results"] = search_result["messages"][-1].content

        if not state["search_results"]:
            raise ValueError("Search agent returned empty results.")

        print("\nSearch completed successfully!")

    except Exception as e:
        print("SEARCH AGENT ERROR:", str(e))
        state["error"] = f"Search failed: {str(e)}"
        return state

        # ==========================================
    # STEP 2 - READER (direct scraping, no LLM)
    # ==========================================

    print("\n" + "=" * 50)
    print("Step 2 - Reader is scraping resources...")
    print("=" * 50)

    try:
        # Pull URLs out of the search output, dedupe, keep order
        urls = re.findall(r"URL:\s*(https?://\S+)", state["search_results"])

        seen = set()
        unique_urls = []
        for u in urls:
            key = u.rstrip("/")
            if key not in seen:
                seen.add(key)
                unique_urls.append(u)

        unique_urls = unique_urls[:3]   # scrape at most 3 pages

        pages = []
        for u in unique_urls:
            content = scrape_url.invoke({"url": u})
            pages.append(f"SOURCE: {u}\n{content}")

        state["scraped_content"] = "\n\n".join(pages)

        if not state["scraped_content"]:
            state["scraped_content"] = (
                "No webpage content could be scraped. "
                "Use the available search results for the report."
            )

        print("\nReader completed!")

    except Exception as e:
        print("READER ERROR:", str(e))
        state["scraped_content"] = (
            f"Webpage scraping failed: {str(e)}. "
            "Use the available search results for the report."
        )

    # ==========================================
    # STEP 3 - WRITER CHAIN
    # ==========================================

    print("\n" + "=" * 50)
    print("Step 3 - Writer is drafting the report...")
    print("=" * 50)

    try:
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        print("\nReport generated successfully!")

    except Exception as e:
        print("WRITER ERROR:", str(e))
        state["error"] = f"Report generation failed: {str(e)}"
        return state

    # ==========================================
    # STEP 4 - CRITIC CHAIN
    # ==========================================

    print("\n" + "=" * 50)
    print("Step 4 - Critic is reviewing the report...")
    print("=" * 50)

    try:
        feedback = ""

        # Retry a few times in case the model returns empty content
        for attempt in range(1, 4):
            feedback = critic_chain.invoke({
                "report": state["report"][:8000]   # keep the prompt small
            }).strip()

            if feedback:
                break

            print(f"Critic returned empty output (attempt {attempt}/3), retrying...")

        if feedback:
            state["feedback"] = feedback
            print("\nCritic review completed!")
            print("\nCritic Feedback:\n", feedback)
        else:
            state["feedback"] = ""
            state["critic_error"] = "Critic model returned empty output after 3 attempts."
            print("CRITIC ERROR:", state["critic_error"])

    except Exception as e:
        print("CRITIC ERROR:", str(e))
        state["feedback"] = ""
        state["critic_error"] = str(e)


    # ==========================================
    # STEP 5 - RETURN FINAL STATE
    # ==========================================

    print("\n" + "=" * 50)
    print("NEXUS AI Research Pipeline Completed!")
    print("=" * 50)

    return state

