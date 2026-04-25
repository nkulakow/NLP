import json

from crewai.tools import tool

from src.services.finnhub.finnhub_sentiment import FinnhubSentimentAnalyser


analyser = FinnhubSentimentAnalyser()


@tool
def analyse_finnhub_sentiment(
    stock_symbol: str, 
    days_back: int = 30, 
    news_count: int = 50
) -> str:
    """
    Analyzes comprehensive market sentiment for a given stock using Finnhub API.
    
    This tool combines multiple data sources to provide a holistic sentiment analysis:
    - Company news sentiment from financial news articles
    - Social media sentiment from Reddit and Twitter
    - Analyst recommendations and ratings
    
    The analysis provides both quantitative metrics and qualitative insights about
    market perception of the stock.
    
    Args:
        stock_symbol (str): The stock ticker symbol to analyze (e.g., 'AAPL', 'TSLA').
        days_back (int): Number of days to look back for news articles (default: 30).
        news_count (int): Maximum number of news articles to analyze (default: 50).
    
    Returns:
        str: A JSON string containing comprehensive sentiment analysis including:
            - Overall sentiment score and label (Bullish/Bearish/Neutral)
            - News sentiment breakdown (positive/neutral/negative counts)
            - Social media sentiment scores from Reddit and Twitter
            - Analyst recommendation distribution
            - Human-readable summary of findings
    
    Example:
        >>> analyse_finnhub_sentiment("AAPL", days_back=30, news_count=50)
        {
            "overall_sentiment": {
                "sentiment_label": "Bullish",
                "overall_score": 0.42,
                "confidence": "High"
            },
            "news_sentiment": {
                "positive_count": 35,
                "neutral_count": 10,
                "negative_count": 5
            },
            ...
        }
    """
    try:
        sentiment_data = analyser.analyse(
            symbol=stock_symbol.upper(),
            days_back=days_back,
            news_count=news_count
        )
        return json.dumps(sentiment_data, indent=2)
    except Exception as e:
        error_response = {
            "error": str(e),
            "message": f"Failed to analyze sentiment for {stock_symbol}. "
                      "Please check if the stock symbol is valid and Finnhub API key is configured."
        }
        return json.dumps(error_response, indent=2)
