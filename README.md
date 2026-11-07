# NEXUS AI

NEXUS AI is an open-source, multi-agent research assistant. Enter a research topic in the Streamlit interface and the system searches the web, extracts useful webpage content, writes a structured report, and evaluates the result.

## Features

- Web research powered by Tavily Search
- Four-stage research workflow:
  - **Search Agent** finds relevant sources
  - **Reader** extracts readable content from up to three source pages
  - **Writer** creates a structured research report
  - **Critic** scores the report and suggests improvements
- Streamlit dashboard with report, source, scraped-content, and critic-review tabs
- Downloadable Markdown research reports
- Graceful handling of search, scraping, and model failures

## Technology stack

- **Python** - application language
- **Streamlit** - interactive web application
- **LangChain** - agents, prompts, tools, and model pipelines
- **LangGraph / LangChain agents** - agent orchestration primitives
- **Groq** - large language model provider through `langchain-groq`
- **Tavily** - web search API
- **Requests** - HTTP requests for source pages
- **Trafilatura** - primary article-content extraction
- **Readability-lxml and BeautifulSoup** - fallback extraction and HTML cleaning
- **python-dotenv** - local environment configuration

## Requirements

- Python 3.10 or newer
- A [Groq API key](https://console.groq.com/)
- A [Tavily API key](https://app.tavily.com/)

## Installation

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/shanmendrasaigajula-123/multi-agent-system.git
   cd multi-agent-system
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

   Never commit `.env` or expose API keys in source code. The repository's `.gitignore` is configured for local environment files.

## Running the application

Start the Streamlit application from the project root:

```bash
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in a browser, enter a topic, and select **Generate Research**.

For a simple command-line pipeline run, edit the sample topic in `main.py` and run:

```bash
python main.py
```

## Architecture

```text
User
  |
  v
Streamlit UI (app.py)
  |
  v
Research pipeline (src/pipelines/pipeline.py)
  |
  +--> Search Agent ----> Tavily Search API
  |
  +--> Reader ----------> HTTP fetch + Trafilatura/Readability/BeautifulSoup
  |
  +--> Writer ----------> Groq LLM via LangChain
  |
  +--> Critic ----------> Groq LLM via LangChain
  |
  v
Research report, sources, scraped content, and feedback
```

The pipeline keeps the intermediate results in a shared state dictionary. Search failures stop the run, while scraping and critic failures are surfaced in the final state so the report can still be displayed when possible.

## Project structure

```text
.
├── app.py                         # Streamlit user interface
├── main.py                        # Optional command-line pipeline entry point
├── requirements.txt               # Python dependencies
├── src/
│   ├── agents/
│   │   └── agents.py              # Groq models, agents, writer, and critic chains
│   ├── pipelines/
│   │   └── pipeline.py            # End-to-end research workflow
│   └── tools/
│       └── tools.py               # Tavily search and webpage scraping tools
└── LICENSE
```

## Contributing

Contributions are welcome. To get started:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`
3. Make and test your changes.
4. Open a pull request with a clear description of the problem and solution.

Please avoid committing credentials, generated files, or local virtual environments.

## License

This project is distributed under the license in [LICENSE](LICENSE).
