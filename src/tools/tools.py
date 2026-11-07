from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re


load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:

    """Search the web using Tavily and return relevant results."""


    results = tavily.search(query,max_results = 5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    return "\n-------\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrape a webpage and extract its readable text content."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        print(f"\nScraping URL: {url}")

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        html = response.text

        # Strategy 1: Trafilatura

        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True
        )

        if extracted and len(extracted.strip()) > 200:

            cleaned = re.sub(r'\s+', ' ', extracted)

            print("Successfully extracted using Trafilatura")

            return cleaned[:3000]

        # Strategy 2: Readability + BeautifulSoup

        doc = Document(html)

        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script", "style", "nav",
            "footer", "header", "aside", "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:

            cleaned = re.sub(r'\s+', ' ', text)

            print("Successfully extracted using Readability")

            return cleaned[:3000]

        return "Unable to extract meaningful content from this webpage."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error: {str(e)}"

    except Exception as e:
        return f"Scraping failed: {str(e)}"

