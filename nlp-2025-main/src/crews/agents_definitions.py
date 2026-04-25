from crewai import Agent, LLM

from src.tools.reddit_sentiment_analysis_tool import analyse_reddit
from src.tools.yahoo_analysis_tool import fetch_yahoo_analysis
from src.tools.yahoo_fundamental_analysis_tool import analyse_fundamentals
from src.tools.yahoo_news_tool import fetch_yahoo_news
from src.tools.yahoo_technical_analysis_tool import analyse_technical_indicators
from src.tools.finnhub_sentiment_tool import analyse_finnhub_sentiment
from src.tools.alphavantage_tools import analyse_alphavantage_sentiment


def create_researcher_agent(llm: LLM) -> Agent:
    """Create Researcher agent for data gathering and sentiment analysis."""
    return Agent(
        role="Senior Stock Market Researcher",
        goal="Gather and analyze comprehensive data about {stock_symbol}",
        backstory="With a Ph.D. in Financial Economics and 15 years of experience in equity research, you're known for meticulous data collection and insightful analysis.",
        llm=llm,
        tools=[analyse_finnhub_sentiment, analyse_alphavantage_sentiment, fetch_yahoo_news, fetch_yahoo_analysis],
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )


def create_technical_analyst_agent(llm: LLM) -> Agent:
    """Create Technical Analyst agent."""
    return Agent(
        role="Expert Technical Analyst",
        goal="Perform an in-depth technical analysis on {stock_symbol}",
        verbose=True,
        memory=True,
        backstory="As a Chartered Market Technician (CMT) with 15 years of experience, you have a keen eye for chart patterns and market trends.",
        tools=[analyse_technical_indicators],
        llm=llm,
        allow_code_execution=False,
    )


def create_fundamental_analyst_agent(llm: LLM) -> Agent:
    """Create Fundamental Analyst agent."""
    return Agent(
        role="Senior Fundamental Analyst",
        goal="Conduct a comprehensive fundamental analysis of {stock_symbol}",
        verbose=True,
        memory=True,
        backstory="With a CFA charter and 15 years of experience in value investing, you dissect financial statements and identify key value drivers.",
        tools=[analyse_fundamentals],
        llm=llm,
        allow_code_execution=False,
    )


def create_reporter_agent(llm: LLM) -> Agent:
    """Create Reporter/Investment Strategist agent."""
    return Agent(
        role="Chief Investment Strategist",
        goal="Synthesize all analyses to create a definitive investment report on {stock_symbol}",
        verbose=True,
        memory=True,
        backstory="As a seasoned investment strategist with 20 years of experience, you weave complex financial data into compelling investment narratives.",
        llm=llm,
        allow_code_execution=False,
    )


def create_sceptic_agent(llm: LLM) -> Agent:
    """Create Sceptic (Devil's Advocate) agent for group chat."""
    return Agent(
        role="Devil's Advocate - Sceptic",
        goal="Challenge assumptions, identify risks, and point out potential weaknesses in the investment thesis for {stock_symbol}",
        backstory="You are a critical thinker who specializes in identifying hidden risks, flawed logic, and overlooked downsides. Your role is to ensure the team doesn't fall into confirmation bias.",
        llm=llm,
        tools=[],
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )


def create_trust_agent(llm: LLM) -> Agent:
    """Create Trust/Data Verification Specialist agent for group chat."""
    return Agent(
        role="Data Verification Specialist - Trust Builder",
        goal="Verify data accuracy, validate source credibility, and ensure all claims are well-substantiated for {stock_symbol}",
        backstory="You are meticulous about data integrity and source verification. Your expertise ensures that conclusions are grounded in reliable, well-documented evidence and not speculation.",
        llm=llm,
        tools=[],
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )


def create_leader_agent(llm: LLM) -> Agent:
    """Create Leader/Discussion Moderator agent for group chat."""
    return Agent(
        role="Discussion Moderator & Chief Synthesizer",
        goal="Moderate the team discussion, synthesize all perspectives into a cohesive final report for {stock_symbol}. ALWAYS end by asking for final advice from Trust Agent and Sceptic Agent before making final recommendation. Use all available agents to provide information for example Senior Stock Market Researcher, Expert Technical Analyst, Senior Fundamental Analyst.",
        backstory="As a senior investment strategist with 20 years of experience, you excel at extracting the strongest arguments from debate, integrating diverse perspectives, and forging consensus on a clear investment recommendation. Your approach: gather all perspectives → delegate to specialists → always consult Trust Agent for data verification → always consult Sceptic Agent for risks → synthesize into final recommendation.",
        llm=llm,
        tools=[],
        verbose=True,
        memory=True,
        allow_code_execution=False,
        allow_delegation=True,
    )
