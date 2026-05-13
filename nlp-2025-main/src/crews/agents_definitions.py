from crewai import Agent, LLM

from src.tools.reddit_sentiment_analysis_tool import analyse_reddit
from src.tools.yahoo_analysis_tool import fetch_yahoo_analysis
from src.tools.yahoo_fundamental_analysis_tool import analyse_fundamentals
from src.tools.yahoo_news_tool import fetch_yahoo_news
from src.tools.yahoo_technical_analysis_tool import analyse_technical_indicators
from src.tools.finnhub_sentiment_tool import analyse_finnhub_sentiment
from src.tools.alphavantage_tools import analyse_alphavantage_sentiment


def create_researcher_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Researcher agent for data gathering and sentiment analysis."""
    tools = [analyse_finnhub_sentiment, analyse_alphavantage_sentiment, fetch_yahoo_news, fetch_yahoo_analysis]
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Senior Stock Market Researcher",
        goal="Gather and analyze comprehensive data about {stock_symbol} with structured findings that team members will reference",
        backstory=(
            "With a Ph.D. in Financial Economics and 15 years of experience in equity research, "
            "you're known for meticulous data collection and insightful analysis. "
            "You structure each data point clearly so other analysts can build upon it with precision. "
            "Include specific metrics, sources, and confidence levels in your findings."
        ),
        llm=llm,
        tools=tools,
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )


def create_technical_analyst_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Technical Analyst agent."""
    tools = [analyse_technical_indicators]
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Expert Technical Analyst",
        goal="Perform an in-depth technical analysis on {stock_symbol} with key levels, trends, and signals clearly documented",
        verbose=True,
        memory=True,
        backstory=(
            "As a Chartered Market Technician (CMT) with 15 years of experience, you have a keen eye for chart patterns and market trends. "
            "You document support/resistance levels, technical signals, and price trends clearly with specific values and dates. "
            "Include indicator values, thresholds, and exact price levels so other team members can validate and challenge your analysis."
        ),
        tools=tools,
        llm=llm,
        allow_code_execution=False,
    )


def create_fundamental_analyst_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Fundamental Analyst agent."""
    tools = [analyse_fundamentals]
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Senior Fundamental Analyst",
        goal="Conduct a comprehensive fundamental analysis of {stock_symbol} with financial metrics, valuation, and health scores",
        verbose=True,
        memory=True,
        backstory=(
            "With a CFA charter and 15 years of experience in value investing, you dissect financial statements and identify key value drivers. "
            "You structure your findings with clear metrics, ratios, and valuations. "
            "Include all specific numbers and comparisons so the team can evaluate the company holistically and verify your work."
        ),
        tools=tools,
        llm=llm,
        allow_code_execution=False,
    )


def create_reporter_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Reporter/Investment Strategist agent."""
    tools = []
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Chief Investment Strategist",
        goal="Synthesize all analyses to create a definitive investment report on {stock_symbol}",
        verbose=True,
        memory=True,
        backstory="As a seasoned investment strategist with 20 years of experience, you weave complex financial data into compelling investment narratives.",
        llm=llm,
        tools=tools,
        allow_code_execution=False,
    )


def create_sceptic_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Sceptic (Devil's Advocate) agent for group chat."""
    tools = []
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Devil's Advocate - Sceptic",
        goal=(
            "Challenge assumptions and identify risks for {stock_symbol}. "
            "Reference specific data points from peer analyses. "
            "For each risk, cite exact evidence and assign probability assessments."
        ),
        backstory=(
            "You are a critical thinker who specializes in identifying hidden risks, flawed logic, and overlooked downsides. "
            "Your role is to ensure the team doesn't fall into confirmation bias. "
            "IMPORTANT: Always cite specific data when raising concerns (e.g., 'P/E of 35 vs industry avg 22 = 59% premium'). "
            "Don't dismiss data; contextualize and challenge interpretations while preserving all data fidelity. "
            "Assign probability levels (High/Medium/Low) to each risk with reasoning."
        ),
        llm=llm,
        tools=tools,
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )


def create_trust_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Trust/Data Verification Specialist agent for group chat."""
    tools = []
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Data Verification Specialist - Trust Builder",
        goal=(
            "Verify data accuracy and validate claims for {stock_symbol}. "
            "Cross-check information across all analyses. "
            "Identify contradictions and confirm source credibility."
        ),
        backstory=(
            "You are meticulous about data integrity and source verification. "
            "Your expertise ensures that conclusions are grounded in reliable, well-documented evidence. "
            "Cross-reference data points across analyses and flag any inconsistencies with specific citations. "
            "Your verification enables the team to have confidence in the final recommendation."
        ),
        llm=llm,
        tools=tools,
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )


def create_leader_agent(llm: LLM, extra_tools: list | None = None) -> Agent:
    """Create Leader/Discussion Moderator agent for group chat."""
    tools = []
    if extra_tools:
        tools.extend(extra_tools)

    return Agent(
        role="Discussion Moderator & Chief Synthesizer",
        goal=(
            "Synthesize all team perspectives into a cohesive final report for {stock_symbol}. "
            "Ensure all data is preserved and verified. "
            "Resolve conflicts using verified data. "
            "ALWAYS consult Trust Agent for verification and Sceptic Agent for risks before final recommendation."
        ),
        backstory=(
            "As a senior investment strategist with 20 years of experience, you excel at extracting the strongest arguments from debate, "
            "integrating diverse perspectives, and forging consensus on a clear investment recommendation. "
            "Your approach: (1) Gather all team perspectives → (2) Consult verified data from specialists → "
            "(3) Delegate to specialists for clarification → (4) Always get Trust Agent verification → "
            "(5) Always address Sceptic Agent concerns → (6) Synthesize into final recommendation with full evidence. "
            "Cite specific metrics and evidence for all conclusions to maintain data richness in the final report."
        ),
        llm=llm,
        tools=tools,
        verbose=True,
        memory=True,
        allow_code_execution=False,
        allow_delegation=True,
    )
