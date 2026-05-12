from typing import List, Optional, Any
from crewai import Agent, LLM

from src.tools.yahoo_analysis_tool import fetch_yahoo_analysis
from src.tools.yahoo_fundamental_analysis_tool import analyse_fundamentals
from src.tools.yahoo_news_tool import fetch_yahoo_news
from src.tools.yahoo_technical_analysis_tool import analyse_technical_indicators
from src.tools.finnhub_sentiment_tool import analyse_finnhub_sentiment
from src.tools.alphavantage_tools import analyse_alphavantage_sentiment

def create_researcher_agent(llm: LLM, extra_tools: Optional[List[Any]] = None) -> Agent:
    base_tools = [
        analyse_finnhub_sentiment,
        analyse_alphavantage_sentiment,
        fetch_yahoo_news,
        fetch_yahoo_analysis
    ]
    if extra_tools:
        base_tools.extend(extra_tools)

    return Agent(
        role="Senior Stock Market Researcher",
        goal="Gather and analyze comprehensive data about {stock_symbol} with structured findings.",
        backstory=(
            "With a Ph.D. in Financial Economics, you are meticulous about data. "
            "You must save all key findings to shared memory using the provided tools."
        ),
        llm=llm,
        tools=base_tools,
        verbose=True,
        memory=True
    )

def create_technical_analyst_agent(llm: LLM, extra_tools: Optional[List[Any]] = None) -> Agent:
    base_tools = [analyse_technical_indicators]
    if extra_tools:
        base_tools.extend(extra_tools)

    return Agent(
        role="Expert Technical Analyst",
        goal="Perform in-depth technical analysis on {stock_symbol}.",
        backstory="Chartered Market Technician (CMT). You document exact price levels and trends.",
        tools=base_tools,
        llm=llm,
        verbose=True,
        memory=True
    )

def create_fundamental_analyst_agent(llm: LLM, extra_tools: Optional[List[Any]] = None) -> Agent:
    base_tools = [analyse_fundamentals]
    if extra_tools:
        base_tools.extend(extra_tools)

    return Agent(
        role="Senior Fundamental Analyst",
        goal="Conduct comprehensive fundamental analysis of {stock_symbol}.",
        backstory="CFA charterholder. You dissect financial statements and valuation ratios.",
        tools=base_tools,
        llm=llm,
        verbose=True,
        memory=True
    )

def create_sceptic_agent(llm: LLM, extra_tools: Optional[List[Any]] = None) -> Agent:
    base_tools = []
    if extra_tools:
        base_tools.extend(extra_tools)

    return Agent(
        role="Devil's Advocate - Sceptic",
        goal="Challenge assumptions and identify risks for {stock_symbol}.",
        backstory="Specialist in identifying hidden risks and confirmation bias.",
        llm=llm,
        tools=base_tools,
        verbose=True,
        memory=True
    )

def create_trust_agent(llm: LLM, extra_tools: Optional[List[Any]] = None) -> Agent:
    base_tools = []
    if extra_tools:
        base_tools.extend(extra_tools)

    return Agent(
        role="Data Verification Specialist",
        goal="Verify data accuracy and validate claims for {stock_symbol}.",
        backstory="Meticulous about data integrity. You cross-reference findings for inconsistencies.",
        llm=llm,
        tools=base_tools,
        verbose=True,
        memory=True
    )

def create_reporter_agent(llm: LLM, extra_tools: Optional[List[Any]] = None) -> Agent:
    base_tools = []
    if extra_tools:
        base_tools.extend(extra_tools)

    return Agent(
        role="Discussion Moderator & Chief Synthesizer",
        goal="Synthesize team perspectives into a final report for {stock_symbol}.",
        backstory="Senior strategist who ensures verified data drives the final recommendation.",
        llm=llm,
        tools=base_tools,
        verbose=True,
        memory=True,
        allow_delegation=True
    )