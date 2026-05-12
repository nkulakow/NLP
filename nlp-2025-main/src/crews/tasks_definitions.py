from crewai import Task, Agent
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.crews.shared_memory import SharedAnalysisMemory


class TaskType(Enum):
    """Enumeration of available task types."""
    RESEARCH = "research"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    REPORTING = "reporting"
    SCEPTIC = "sceptic"
    TRUST = "trust"
    SYNTHESIS = "synthesis"
    RESEARCH_REFINEMENT = "research_refinement"
    TECHNICAL_REFINEMENT = "technical_refinement"
    FUNDAMENTAL_REFINEMENT = "fundamental_refinement"


# Task configurations
TASK_CONFIGS = {
    TaskType.RESEARCH: {
        "description": (
            "Gather and analyze qualitative data and public sentiment for '{stock_symbol}' "
            "by processing Reddit discussions (using analyse_reddit_tool), "
            "at least 20 Yahoo News articles (using fetch_yahoo_news_tool), "
            "and Yahoo financial analyses (using fetch_yahoo_analysis_tool). "
            "Focus on identifying the *drivers* of sentiment and the *impact* of news. "
            "Synthesize this information to build a comprehensive picture of the current "
            "sentiment and news landscape surrounding the stock. "
            "If shared memory is available, store your findings using update_sentiment_memory(key, value, subsection='', reasoning). "
            "Use empty subsection for top-level sentiment data like overall_sentiment and confidence. "
            "Write overall_sentiment, confidence, key themes, and supporting evidence into shared memory."
        ),
        "expected_output": (
            "A textual report summarizing the current public sentiment, relevant news, "
            "and analyst opinions surrounding '{stock_symbol}'. This report **must**:\n"
            "1.  Provide a concise overview of the general sentiment (positive, negative, mixed) and **highlight the key themes or topics driving this sentiment** based on Reddit analysis.\n"
            "2.  Summarize the **most impactful recent news articles** from Yahoo Finance, explaining their potential implications for the stock.\n"
            "3.  Briefly discuss the consensus from Yahoo financial analyses (e.g., earnings estimates, analyst ratings) and **point out any notable shifts or strong opinions**.\n"
            "4.  Conclude with a **short, insightful synthesis** of these findings, focusing on the overall sentiment narrative.\n"
            "If shared memory is enabled, also persist the key sentiment values into shared memory."
        ),
    },
    TaskType.TECHNICAL_ANALYSIS: {
        "description": (
            "Perform an in-depth technical analysis of '{stock_symbol}' by fetching "
            "historical market data and calculating a wide array of technical indicators "
            "(using analyse_technical_indicators_tool). Your primary goal is to **interpret these indicators** "
            "to identify trends, patterns, support/resistance levels, and potential trading signals, "
            "explaining their significance. "
            "If shared memory is available, store your analysis using update_technical_memory(key, value, subsection='', reasoning). "
            "Write price_trend, overall_outlook, confidence, key levels, and signal summaries into shared memory."
        ),
        "expected_output": (
            "A detailed textual technical analysis report for '{stock_symbol}'. This report **must**:\n"
            "1.  Begin with an overview of the current price trend (e.g., uptrend, downtrend, consolidation) and its strength.\n"
            "2.  **Interpret the signals from key technical indicators** (like SMAs, EMAs, MACD, RSI, Bollinger Bands, Stochastics). For each indicator, explain what its current state suggests for the stock (e.g., 'RSI at 75 indicates overbought conditions, suggesting a potential pullback.').\n"
            "3.  Identify and describe any significant chart patterns observed (e.g., head and shoulders, double top/bottom) and their implications.\n"
            "4.  Clearly state key support and resistance levels and their importance.\n"
            "5.  Highlight any notable bullish or bearish signals or divergences, explaining the reasoning.\n"
            "6.  Conclude with a **summary of the overall technical outlook** for the stock (e.g., bullish, bearish, neutral with key levels to watch).\n"
            "The report should be purely textual and focus on insights and highlights, not raw data dumps.\n"
            "If shared memory is enabled, record the core technical findings in shared memory as structured data."
        ),
    },
    TaskType.FUNDAMENTAL_ANALYSIS: {
        "description": (
            "Conduct a comprehensive fundamental analysis of '{stock_symbol}' by fetching "
            "and analyzing its financial statements (income, balance sheet, cash flow), "
            "earnings reports, and company overview from Yahoo Finance (using analyse_fundamentals_tool). "
            "Your focus is to **interpret this data** to assess its financial health, profitability, "
            "growth prospects, valuation, and overall intrinsic value, highlighting key strengths and weaknesses. "
            "If shared memory is available, store your findings using update_fundamental_memory(key, value, subsection='', reasoning). "
            "Write valuation_assessment, health_score, overall_outlook, and key financial metrics into shared memory."
        ),
        "expected_output": (
            "A detailed textual fundamental analysis report for '{stock_symbol}'. This report **must**:\n"
            "1.  Provide a summary of the company's business model and its current market position based on the overview.\n"
            "2.  Analyze and **interpret key financial metrics and ratios** (e.g., P/E, P/S, Debt-to-Equity, ROE, profit margins) and compare them to historical values or industry peers if possible (even if qualitatively).\n"
            "3.  Discuss trends in revenue, earnings, and cash flow, **highlighting growth drivers or areas of concern**.\n"
            "4.  Assess the company's financial health, focusing on liquidity, solvency, and profitability.\n"
            "5.  Provide an **assessment of the stock's valuation** (e.g., appearing overvalued, undervalued, or fairly valued based on the analysis) and explain the reasoning.\n"
            "6.  Conclude with a **summary of the key fundamental strengths and weaknesses** and the overall fundamental outlook for the company.\n"
            "The report should be purely textual and focus on insights and highlights, not raw data dumps.\n"
            "If shared memory is enabled, record the essential fundamental findings in shared memory as structured data."
        ),
    },
    TaskType.REPORTING: {
        "description": (
            "Synthesize the sentiment analysis, technical analysis, and fundamental analysis "
            "for '{stock_symbol}', drawing from the outputs of the Stock Sentiment Agent, "
            "Technical Analyst, and Fundamental Analyst. Your goal is to formulate a cohesive, "
            "insightful, and definitive investment report. **Do not simply concatenate previous reports.** "
            "Instead, integrate these diverse insights, critically evaluate them, "
            "highlight the most crucial findings and any convergences or divergences, "
            "discuss potential risks and rewards, and provide a clear, actionable investment thesis."
        ),
        "expected_output": (
            "A comprehensive and well-structured textual investment report for '{stock_symbol}'. "
            "This report **must**:\n"
            "1.  Begin with a concise **Executive Summary** that states the overall investment thesis (e.g., Buy, Sell, Hold with price targets if applicable) and the key reasons supporting it.\n"
            "2.  **Synthesize and critically evaluate** key findings from the sentiment analysis. Highlight how public perception and news flow might impact the stock, going beyond just stating the sentiment.\n"
            "3.  **Synthesize and critically evaluate** key findings from the technical analysis. Explain how the technical outlook aligns or contrasts with other analyses and what key levels are critical.\n"
            "4.  **Synthesize and critically evaluate** key findings from the fundamental analysis. Discuss the core financial health and valuation in the context of the overall investment thesis.\n"
            "5.  **Identify and discuss convergences or divergences** between the sentiment, technical, and fundamental analyses. For example, 'While fundamentals appear strong, technical indicators suggest short-term caution.'\n"
            "6.  Clearly outline the **primary catalysts and risk factors** for the stock.\n"
            "7.  Conclude with a **well-reasoned investment outlook and a specific recommendation**, reiterating the main supporting points. The recommendation should be actionable.\n"
            "This report should be a narrative, not just a list of points. Strive for clarity, conciseness, and actionable insights."
        ),
    },
    TaskType.SCEPTIC: {
        "description": (
            "Play devil's advocate for '{stock_symbol}' investment thesis. "
            "Identify risks, weaknesses, potential downsides, and challenges to the bullish case. "
            "Challenge assumptions made by other analysts. Be critical and thorough. "
            "If shared memory is available, persist the risks using add_risk_memory(risk_description, evidence, probability, mitigation)."
        ),
        "expected_output": (
            "Critical analysis highlighting risks, weaknesses, potential problems, and downsides "
            "for '{stock_symbol}'. Focus on what could go wrong and alternative bearish scenarios.\n"
            "When shared memory is enabled, add these identified risks to shared memory."
        ),
    },
    TaskType.TRUST: {
        "description": (
            "Verify data credibility and validate claims about '{stock_symbol}'. "
            "Cross-check information across sentiment, technical, and fundamental analyses. "
            "Confirm source reliability and data accuracy. "
            "If shared memory is available, store the verification results using add_verification_memory(claim, verified, reasoning)."
        ),
        "expected_output": (
            "Data verification report confirming accuracy and reliability of sources used "
            "in the analysis of '{stock_symbol}'.\n"
            "When shared memory is enabled, persist verification outcomes to shared memory."
        ),
    },
    TaskType.SYNTHESIS: {
        "description": (
            "You are the investment committee leader. Synthesize all perspectives on '{stock_symbol}' "
            "from Researcher, Technical Analyst, Fundamental Analyst, Sceptic, and Trust Specialist. "
            "Integrate their insights, resolve conflicts, address sceptic concerns, and create a final consensus report. "
            "Provide clear investment recommendation (Buy/Sell/Hold) with price target. "
            "If shared memory is enabled, consult shared memory and base your recommendation on the documented evidence."
        ),
        "expected_output": (
            "Comprehensive investment report including executive summary, sentiment analysis, technical analysis, "
            "fundamental analysis, risk assessment, convergences/divergences, catalysts, and final recommendation.\n"
            "When shared memory is enabled, use shared memory data as the evidence basis for your final recommendation."
        ),
    },
    TaskType.RESEARCH_REFINEMENT: {
        "description": (
            "Review and refine your initial research analysis for '{stock_symbol}' based on the initial findings "
            "from Technical Analyst and Fundamental Analyst. Look for additional context, verify claims, "
            "and identify any sentiment drivers that may have been missed. Consider how technical and fundamental "
            "data might influence or contradict the sentiment narrative you initially identified."
        ),
        "expected_output": (
            "A refined research report that incorporates insights from technical and fundamental analysis. "
            "Highlight any new sentiment drivers discovered, verify or correct initial findings, "
            "and explain how technical/fundamental data impacts the overall sentiment assessment."
        ),
    },
    TaskType.TECHNICAL_REFINEMENT: {
        "description": (
            "Refine your technical analysis of '{stock_symbol}' by incorporating insights from the initial "
            "Research and Fundamental analysis. Re-evaluate your technical indicators in light of the "
            "sentiment landscape and fundamental health. Look for confirmation or contradiction between "
            "technical signals and the broader market context."
        ),
        "expected_output": (
            "A refined technical analysis that integrates research and fundamental insights. "
            "Reassess key levels, trends, and signals considering the sentiment and fundamental context. "
            "Highlight any technical patterns that align with or contradict the broader analysis."
        ),
    },
    TaskType.FUNDAMENTAL_REFINEMENT: {
        "description": (
            "Refine your fundamental analysis of '{stock_symbol}' by considering the initial Research "
            "and Technical analysis findings. Evaluate how market sentiment and technical trends "
            "might impact your fundamental valuation. Look for catalysts or risks that could affect "
            "your fundamental assessment."
        ),
        "expected_output": (
            "A refined fundamental analysis that incorporates research and technical insights. "
            "Reassess valuation metrics, growth prospects, and risk factors in light of sentiment "
            "and technical trends. Provide updated investment thesis considering all perspectives."
        ),
    },
}


def create_task(
    task_type: TaskType,
    agent: Agent,
    context: Optional[list] = None,
    shared_memory: Optional["SharedAnalysisMemory"] = None,
) -> Task:
    """
    Factory function to create tasks based on type.

    Args:
        task_type: The type of task to create (TaskType enum).
        agent: The agent that will execute the task.
        context: Optional context list for tasks that require previous outputs.
        shared_memory: Optional shared memory instance for group chat mode.

    Returns:
        A configured Task instance.

    Raises:
        ValueError: If task_type is not a valid TaskType.
    """
    if not isinstance(task_type, TaskType):
        raise ValueError(f"Invalid task type: {task_type}. Must be a TaskType enum value.")

    config = TASK_CONFIGS.get(task_type)
    if not config:
        raise ValueError(f"No configuration found for task type: {task_type}")

    task_kwargs = {
        "description": config["description"],
        "expected_output": config["expected_output"],
        "agent": agent,
    }

    # Note: Do NOT add shared memory summary to task description at creation time
    # Tasks should be executed first, then memory summary checked after execution
    # This prevents showing empty memory status in task instructions

    # Add context if provided
    if context is not None:
        task_kwargs["context"] = context

    return Task(**task_kwargs)
