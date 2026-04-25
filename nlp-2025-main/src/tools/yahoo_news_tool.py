import json

from crewai.tools import tool

from src.services.yahoo_news_fetcher import YahooNewsFetcher


@tool
def fetch_yahoo_news(stock_symbol: str, count: int = 10) -> str:
    """
    Fetches recent news articles related to the given stock symbol from Yahoo Finance.

    Args:
        stock_symbol (str): The stock ticker symbol for which to fetch news articles.
        count (int): The number of news articles to fetch.

    Returns:
        str: A JSON string containing the fetched news articles.
    """
    news_fetcher = YahooNewsFetcher(stock_symbol)
    news_articles = news_fetcher.fetch_news(count=count)
    return json.dumps(news_articles, indent=2)
