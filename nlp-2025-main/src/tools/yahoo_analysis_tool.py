import json

from crewai.tools import tool

from src.services.yahoo_analysis_fetcher import YahooAnalysisFetcher


@tool
def fetch_yahoo_analysis(ticker: str) -> str:
    """
    Fetches various analyses related to the stock ticker. The analyses include:
    - Earnings Estimate
    - Revenue Estimate
    - Growth Estimates
    - Earnings History
    - EPS Trend

    Args:
        ticker (str): The stock ticker symbol to analyze.

    Returns:
        str: A JSON string containing different types of analyses.
    """
    fetcher = YahooAnalysisFetcher(ticker)
    analysis = fetcher.fetch_analysis()

    return json.dumps(analysis, indent=2)
