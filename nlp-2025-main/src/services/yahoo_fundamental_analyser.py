import yfinance as yf


class YahooFundamentalAnalyser:
    def __init__(self, ticker: str):
        self.stock = yf.Ticker(ticker)

    def fetch_fundamentals(self) -> dict:
        """
        Fetches various fundamental data related to the stock ticker.
        Returns:
            dict: A dictionary containing different types of fundamental data.
        """
        return self.stock.get_info()
