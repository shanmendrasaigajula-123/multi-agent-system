from langchain.agents import create_agent 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tenacity import retry, wait_exponential, stop_after_attempt
from src.tools.tools import web_search , scrape_url
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=3
)

# Dedicated model for the critic: low reasoning so the answer isn't starved
critic_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=3,
    reasoning_effort="low",
    max_tokens=2000,
)





# 1st ageent 
def build_search_agent():
    return create_agent(
        model=llm,
        tools = [web_search]
    )

def build_reader_agent():
    return create_agent(
        model=llm,
        tools = [scrape_url]
    )

writer_prompt = ChatPromptTemplate.from_messages([
    ('system', 'you are an expert research writer. Write clear, structured and insightful reports.'),
    ('human', """Write a detailed research report on the topic below.
    
topic: {topic}
Research Gathered:
{research}

Structure the report as:
- Introduction
- key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all sources used in the research)

Be detailed, factual and Proffessional.

""")
])

writer_chain = writer_prompt | llm | StrOutputParser()

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict: ..."""),
])

critic_chain = critic_prompt | critic_llm | StrOutputParser()

