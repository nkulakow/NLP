import json

from crewai.tools import tool

from src.services.yahoo_technical_analyser import YahooTechnicalAnalyser


@tool
def analyse_technical_indicators(ticker: str, period: str = "1y") -> str:
    """
    Fetches and analyses technical indicators for a given stock ticker using Yahoo Finance.
    The analysis includes various technical indicators such as:
    - SMA (Simple Moving Average)
    - EMA (Exponential Moving Average)
    - WMA (Weighted Moving Average)
    - MACD (Moving Average Convergence Divergence)
    - RSI (Relative Strength Index)
    - Stochastic Oscillator
    - Bollinger Bands
    - ATR (Average True Range)

    Args:
        ticker (str): The stock ticker symbol to analyze.
        period (str): The time period for the analysis (default is "1y").
    Returns:

        str: A JSON string containing the fetched technical indicators.
    """
    analyser = YahooTechnicalAnalyser(ticker)
    data: dict = analyser.get_technical_data(period=period)
    return json.dumps(data, indent=2)
