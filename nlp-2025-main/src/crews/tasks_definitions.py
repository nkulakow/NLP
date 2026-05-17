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
            "\n\n"
            "**IMPORTANT - Data Preservation:**\n"
            "- Structure all findings with specific metrics, sources, and confidence levels\n"
            "- Include sentiment scores, key themes, sample quotes, and source citations\n"
            "- Your data will be reviewed and built upon by other team members\n"
            "- Provide enough detail for validation and challenge by peers"
        ),
        "expected_output": (
            "A textual report summarizing the current public sentiment, relevant news, "
            "and analyst opinions surrounding '{stock_symbol}'. This report **must**:\n"
            "1.  Provide a concise overview of the general sentiment (positive, negative, mixed) and **highlight the key themes or topics driving this sentiment** based on Reddit analysis.\n"
            "2.  Summarize the **most impactful recent news articles** from Yahoo Finance, explaining their potential implications for the stock.\n"
            "3.  Briefly discuss the consensus from Yahoo financial analyses (e.g., earnings estimates, analyst ratings) and **point out any notable shifts or strong opinions**.\n"
            "4.  Conclude with a **short, insightful synthesis** of these findings, focusing on the overall sentiment narrative.\n"
            "5.  **Include specific data points** with sources for all claims (e.g., 'Sentiment score: 0.65 from 250 Reddit posts on r/investing').\n"
            "The report should be purely textual and focus on insights and highlights, not raw data dumps."
        ),
    },
    TaskType.TECHNICAL_ANALYSIS: {
        "description": (
            "Perform an in-depth technical analysis of '{stock_symbol}' by fetching "
            "historical market data and calculating a wide array of technical indicators "
            "(using analyse_technical_indicators_tool). Your primary goal is to **interpret these indicators** "
            "to identify trends, patterns, support/resistance levels, and potential trading signals, "
            "explaining their significance."
            "\n\n"
            "**IMPORTANT - Data Preservation:**\n"
            "- Include specific indicator values with thresholds (e.g., 'RSI: 72 (overbought threshold: 70)')\n"
            "- Document exact support/resistance price levels with dates\n"
            "- Cite technical patterns with specific price points and date ranges\n"
            "- Provide current price, trend direction, and key levels clearly\n"
            "- Your analysis will be cross-checked by the Trust Agent and challenged by the Sceptic"
        ),
        "expected_output": (
            "A detailed textual technical analysis report for '{stock_symbol}'. This report **must**:\n"
            "1.  Begin with an overview of the current price trend (e.g., uptrend, downtrend, consolidation) and its strength.\n"
            "2.  **Interpret the signals from key technical indicators** (like SMAs, EMAs, MACD, RSI, Bollinger Bands, Stochastics). For each indicator, explain what its current state suggests for the stock (e.g., 'RSI at 75 indicates overbought conditions, suggesting a potential pullback.').\n"
            "3.  Identify and describe any significant chart patterns observed (e.g., head and shoulders, double top/bottom) and their implications.\n"
            "4.  Clearly state key support and resistance levels and their importance.\n"
            "5.  Highlight any notable bullish or bearish signals or divergences, explaining the reasoning.\n"
            "6.  Conclude with a **summary of the overall technical outlook** for the stock (e.g., bullish, bearish, neutral with key levels to watch).\n"
            "7.  **Include specific numbers and dates** for all claims (e.g., 'Support at $150 (established 2024-03-15), RSI: 65, MACD positive').\n"
            "The report should be purely textual and focus on insights and highlights, not raw data dumps."
        ),
    },
    TaskType.FUNDAMENTAL_ANALYSIS: {
        "description": (
            "Conduct a comprehensive fundamental analysis of '{stock_symbol}' by fetching "
            "and analyzing its financial statements (income, balance sheet, cash flow), "
            "earnings reports, and company overview from Yahoo Finance (using analyse_fundamentals_tool). "
            "Your focus is to **interpret this data** to assess its financial health, profitability, "
            "growth prospects, valuation, and overall intrinsic value, highlighting key strengths and weaknesses."
            "\n\n"
            "**IMPORTANT - Data Preservation:**\n"
            "- Include all key financial ratios with specific values (P/E, P/S, D/E, ROE, margins, etc.)\n"
            "- Compare to historical data and industry averages with precise numbers\n"
            "- Document revenue, earnings, and cash flow trends with percentages and date ranges\n"
            "- Provide clear valuation assessment with supporting multiples\n"
            "- Your metrics will be verified and challenged by peers—ensure precision and context"
        ),
        "expected_output": (
            "A detailed textual fundamental analysis report for '{stock_symbol}'. This report **must**:\n"
            "1.  Provide a summary of the company's business model and its current market position based on the overview.\n"
            "2.  Analyze and **interpret key financial metrics and ratios** (e.g., P/E, P/S, Debt-to-Equity, ROE, profit margins) and compare them to historical values or industry peers if possible (even if qualitatively).\n"
            "3.  Discuss trends in revenue, earnings, and cash flow, **highlighting growth drivers or areas of concern**.\n"
            "4.  Assess the company's financial health, focusing on liquidity, solvency, and profitability.\n"
            "5.  Provide an **assessment of the stock's valuation** (e.g., appearing overvalued, undervalued, or fairly valued based on the analysis) and explain the reasoning.\n"
            "6.  Conclude with a **summary of the key fundamental strengths and weaknesses** and the overall fundamental outlook for the company.\n"
            "7.  **Include all specific ratios and values** (e.g., 'P/E: 28.5 vs industry avg 22.1, ROE: 18.2%, Debt-to-Equity: 0.45').\n"
            "The report should be purely textual and focus on insights and highlights, not raw data dumps."
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
            "Challenge assumptions made by other analysts. Be critical and thorough."
            "\n\n"
            "**CRITICAL - Data Preservation Required:**\n"
            "- For EACH risk, cite specific data points from peer analyses (e.g., 'P/E of 35 vs industry avg 22 = 59% premium')\n"
            "- Do NOT dismiss data; instead contextualize it and challenge interpretations\n"
            "- Example: 'RSI at 72 suggests overbought, BUT volume confirms strength—justify premium'\n"
            "- Reference exact metrics, dates, and sources when raising concerns\n"
            "- Assign probability levels (High/Medium/Low) with reasoning\n"
            "- Preserve all data fidelity—other team members need this context to validate or refute your challenges"
        ),
        "expected_output": (
            "Critical analysis highlighting risks, weaknesses, potential problems, and downsides "
            "for '{stock_symbol}'. This must include:\n"
            "1.  Specific risks with evidence citations (e.g., 'P/E premium of 59% creates valuation risk')\n"
            "2.  Alternative bearish scenarios with supporting logic\n"
            "3.  Probability assessments (High/Medium/Low) for each risk\n"
            "4.  Potential mitigation factors if any\n"
            "Focus on what could go wrong and alternative bearish scenarios, but always cite the underlying data."
        ),
    },
    TaskType.TRUST: {
        "description": (
            "Verify data credibility and validate claims about '{stock_symbol}'. "
            "Cross-check information across sentiment, technical, and fundamental analyses. "
            "Confirm source reliability and data accuracy."
            "\n\n"
            "**CRITICAL - Data Preservation & Verification:**\n"
            "- Cross-reference data points across all analyses for contradictions\n"
            "- Flag any inconsistencies with specific citations (e.g., 'Sceptic cites P/E of 35, but Fundamental reported 33')\n"
            "- Assess source quality for each major claim\n"
            "- Document verified claims with confidence levels (High/Medium/Low)\n"
            "- Preserve complete audit trail—your verification enables confident final recommendation"
        ),
        "expected_output": (
            "Data verification report confirming accuracy and reliability of sources used "
            "in the analysis of '{stock_symbol}'. Must include:\n"
            "1.  Verified claims with confidence levels\n"
            "2.  Any contradictions found with specific citations\n"
            "3.  Data quality assessment for sources\n"
            "4.  Unresolved questions or ambiguities\n"
            "Keep this report detailed and specific—it will guide the final recommendation."
        ),
    },
    TaskType.SYNTHESIS: {
        "description": (
            "You are the investment committee leader. Synthesize all perspectives on '{stock_symbol}' "
            "from Researcher, Technical Analyst, Fundamental Analyst, Sceptic, and Trust Specialist. "
            "Integrate their insights, resolve conflicts, address sceptic concerns, and create a final consensus report. "
            "Provide clear investment recommendation (Buy/Sell/Hold) with price target."
            "\n\n"
            "**Data Preservation Throughout Debate:**\n"
            "- Reference the Trust Agent's verified claims to ensure all recommendations are fact-based\n"
            "- Acknowledge and address each Sceptic risk with specific data points\n"
            "- Cite concrete evidence for all conclusions (e.g., 'P/E of 28 with 15% growth justified Buy')\n"
            "- Preserve data richness—the final report must contain full context from all analyses"
        ),
        "expected_output": (
            "Comprehensive investment report including executive summary, sentiment analysis, technical analysis, "
            "fundamental analysis, risk assessment, convergences/divergences, catalysts, and final recommendation. "
            "The report must be data-rich with specific metrics and evidence for all claims."
        ),
    },
}


def create_task(
    task_type: TaskType,
    agent: Agent,
    context: Optional[list] = None,
    use_shared_memory: bool = False,
) -> Task:
    """
    Factory function to create tasks with forced Shared Memory Tool usage.
    """
    if not isinstance(task_type, TaskType):
        raise ValueError(f"Invalid task type: {task_type}. Must be a TaskType enum value.")

    config = TASK_CONFIGS.get(task_type)
    if not config:
        raise ValueError(f"No configuration found for task type: {task_type}")

    description = config["description"]
    expected_output = config["expected_output"]

    # --- SHARED MEMORY LOGIC ---
    # 1. Define which agents are primary writers
    writing_tasks = [
        TaskType.RESEARCH,
        TaskType.TECHNICAL_ANALYSIS,
        TaskType.FUNDAMENTAL_ANALYSIS,
        TaskType.SCEPTIC,
        TaskType.TRUST
    ]

    # 2. READ instruction (Universal)
    memory_instr = (
        "\n\n**MANDATORY TOOL USAGE:**\n"
        "- **TO READ:** ALWAYS start by calling `memory_tool()` (with no arguments) "
        "to see the current progress of your teammates.\n"
    )

    # 3. WRITE instruction (Task Specific)
    if task_type in writing_tasks:
        category_map = {
            TaskType.RESEARCH: "sentiment",
            TaskType.TECHNICAL_ANALYSIS: "technical",
            TaskType.FUNDAMENTAL_ANALYSIS: "fundamental",
            TaskType.SCEPTIC: "risks",
            TaskType.TRUST: "verifications"
        }
        cat = category_map.get(task_type, "verifications")

        memory_instr += (
            f"- **TO WRITE:** BEFORE finishing, you MUST use `memory_tool` providing "
            f"the 'category' (use '{cat}'), a specific 'key', and the 'value' (your findings). "
            f"Example: memory_tool(category='{cat}', key='metric_name', value='metric_value')\n"
        )

    if use_shared_memory and task_type != TaskType.SYNTHESIS:
        description += memory_instr

    task_kwargs = {
        "description": description,
        "expected_output": expected_output,
        "agent": agent,
    }

    if context is not None:
        task_kwargs["context"] = context

    return Task(**task_kwargs)
