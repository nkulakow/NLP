import json

from crewai.tools import tool

from src.services.yahoo_fundamental_analyser import YahooFundamentalAnalyser


@tool
def analyse_fundamentals(ticker: str) -> str:
    """
    Fetches a comprehensive profile for a given stock ticker.
    This tool retrieves a wide array of information about a publicly traded company,
    encapsulated in a single JSON object. The data includes:
        - General company details: Address, website, industry, sector, business summary, number of employees.
        - Key executives and company officers.
        - Corporate governance risk scores.
        - Current and historical stock performance metrics: Open, high, low, close, volume, market cap, beta.
        - Dividend information: Rate, yield, ex-dividend date, payout ratio.
        - Valuation metrics: Trailing P/E, forward P/E, price-to-sales, price-to-book.
        - Moving averages: 50-day and 200-day averages.
        - Share statistics: Shares outstanding, float, shares short, insider/institutional ownership.
        - Financial highlights: Total cash, total debt, total revenue, profit margins, return on assets/equity, EBITDA.
        - Earnings data: Trailing EPS, forward EPS, earnings quarterly growth.
        - Analyst recommendations: Target prices (high, low, mean, median), recommendation mean, number of opinions.
        - Information about the last stock split.
        - Market state and trading session details.

    Args:
        ticker (str): The stock ticker symbol to analyze.

    Returns:
        str: A JSON string containing the fetched profile data.
    """
    fetcher = YahooFundamentalAnalyser(ticker)
    analysis = fetcher.fetch_fundamentals()

    return json.dumps(analysis, indent=2)
