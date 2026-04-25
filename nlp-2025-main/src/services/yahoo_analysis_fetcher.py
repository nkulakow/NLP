import yfinance as yf


class YahooAnalysisFetcher:
    def __init__(self, ticker: str):
        self.stock = yf.Ticker(ticker)

    def fetch_analysis(self) -> dict:
        """
        Fetches various analyses related to the stock ticker.
        Returns:
            dict: A dictionary containing different types of analyses.
        """
        earnings_estimate = self.stock.get_earnings_estimate()
        revenue_estimate = self.stock.get_revenue_estimate()
        growth_estimates = self.stock.get_growth_estimates()
        earnings_history = self.stock.get_earnings_history()
        earnings_history.index = earnings_history.index.strftime("%Y-%m-%d")
        eps_trend = self.stock.get_eps_trend()

        analysis = {
            "ticker": self.stock.ticker,
            "earnings_estimate": earnings_estimate.to_dict(),
            "revenue_estimate": revenue_estimate.to_dict(),
            "growth_estimates": growth_estimates.to_dict(),
            "earnings_history": earnings_history.to_dict(),
            "eps_trend": eps_trend.to_dict(),
        }
        return analysis
