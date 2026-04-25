from datetime import datetime

import yfinance as yf


class YahooNewsFetcher:
    """
    A class to fetch news articles related to a specific stock ticker from Yahoo Finance.

    Attributes:
        ticker (str): The stock ticker symbol for which to fetch news articles.
    """

    def __init__(self, ticker: str):
        self.stock = yf.Ticker(ticker)

    def fetch_news(self, count: int) -> list:
        """
        Fetches recent news articles related to the stock ticker.

        Args:
            count (int): The number of news articles to fetch.
        Returns:
            list: A list of dictionaries containing news articles with their titles, summaries, sources, and publication dates.
        """
        articles = self.stock.get_news(count=count)

        aggregated_news = []

        for article in articles:
            content: dict = article["content"]

            aggregated_news.append(
                {
                    "title": content.get("title", ""),
                    "summary": content.get("summary", ""),
                    "source": content.get("provider", dict()).get("displayName", ""),
                    "pubDate": datetime.fromisoformat(content.get("pubDate", "")).strftime("%Y-%m-%d"),
                }
            )

        return aggregated_news
