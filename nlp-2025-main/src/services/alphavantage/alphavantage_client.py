import os
from typing import Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()


class AlphaVantageClient:
    """
    Client for interacting with Alpha Vantage API.
    
    Provides methods to fetch company overview, news sentiment, and market data.
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        """Initialize Alpha Vantage client with API key from environment."""
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables")

    def _make_request(self, params: Dict) -> Dict:
        """
        Make API request to Alpha Vantage.
        
        Args:
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        params['apikey'] = self.api_key
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()

    def get_company_overview(self, symbol: str) -> Dict:
        """
        Get comprehensive company overview and fundamentals.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with company information and financial metrics
        """
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol
            }
            data = self._make_request(params)
            
            return {
                'symbol': data.get('Symbol', symbol),
                'name': data.get('Name', 'N/A'),
                'description': data.get('Description', 'N/A'),
                'sector': data.get('Sector', 'N/A'),
                'industry': data.get('Industry', 'N/A'),
                'market_cap': data.get('MarketCapitalization', 'N/A'),
                'pe_ratio': data.get('PERatio', 'N/A'),
                'peg_ratio': data.get('PEGRatio', 'N/A'),
                'dividend_yield': data.get('DividendYield', 'N/A'),
                'eps': data.get('EPS', 'N/A'),
                'revenue_ttm': data.get('RevenueTTM', 'N/A'),
                'profit_margin': data.get('ProfitMargin', 'N/A'),
                'beta': data.get('Beta', 'N/A'),
                '52_week_high': data.get('52WeekHigh', 'N/A'),
                '52_week_low': data.get('52WeekLow', 'N/A'),
                'analyst_target_price': data.get('AnalystTargetPrice', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching company overview: {e}")
            return {'symbol': symbol, 'name': 'N/A'}

    def get_news_sentiment(
        self, 
        tickers: str,
        topics: str = None,
        limit: int = 50
    ) -> Dict:
        """
        Get news and sentiment data from Alpha Vantage.
        
        Args:
            tickers: Comma-separated stock symbols (e.g., 'AAPL,MSFT')
            topics: Optional topics filter (e.g., 'technology,finance')
            limit: Maximum number of news items
            
        Returns:
            Dictionary with news articles and sentiment scores
        """
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': tickers,
                'limit': limit
            }
            
            if topics:
                params['topics'] = topics
            
            data = self._make_request(params)
            
            feed = data.get('feed', [])
            
            articles = []
            sentiment_scores = []
            
            for item in feed:
                # Get ticker-specific sentiment
                ticker_sentiment = None
                for ts in item.get('ticker_sentiment', []):
                    if ts.get('ticker', '').upper() == tickers.split(',')[0].upper():
                        ticker_sentiment = ts
                        break
                
                if ticker_sentiment:
                    sentiment_score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
                    sentiment_label = ticker_sentiment.get('ticker_sentiment_label', 'Neutral')
                    sentiment_scores.append(sentiment_score)
                else:
                    sentiment_score = 0
                    sentiment_label = 'Neutral'
                
                articles.append({
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'source': item.get('source', ''),
                    'url': item.get('url', ''),
                    'time_published': item.get('time_published', ''),
                    'overall_sentiment_score': float(item.get('overall_sentiment_score', 0)),
                    'overall_sentiment_label': item.get('overall_sentiment_label', 'Neutral'),
                    'ticker_sentiment_score': sentiment_score,
                    'ticker_sentiment_label': sentiment_label
                })
            
            # Calculate aggregate sentiment
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            # Count sentiment labels
            sentiment_counts = {
                'Bullish': 0,
                'Somewhat-Bullish': 0,
                'Neutral': 0,
                'Somewhat-Bearish': 0,
                'Bearish': 0
            }
            
            for article in articles:
                label = article['ticker_sentiment_label']
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
            
            return {
                'ticker': tickers.split(',')[0],
                'articles_analyzed': len(articles),
                'average_sentiment_score': round(avg_sentiment, 4),
                'sentiment_distribution': sentiment_counts,
                'articles': articles[:limit]
            }
            
        except Exception as e:
            print(f"Error fetching news sentiment: {e}")
            return {
                'ticker': tickers,
                'articles_analyzed': 0,
                'average_sentiment_score': 0,
                'sentiment_distribution': {},
                'articles': []
            }

    def get_earnings(self, symbol: str) -> Dict:
        """
        Get earnings data for a company.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with quarterly and annual earnings
        """
        try:
            params = {
                'function': 'EARNINGS',
                'symbol': symbol
            }
            data = self._make_request(params)
            
            quarterly = data.get('quarterlyEarnings', [])[:4]  # Last 4 quarters
            annual = data.get('annualEarnings', [])[:3]  # Last 3 years
            
            return {
                'symbol': symbol,
                'quarterly_earnings': [
                    {
                        'fiscal_date_ending': q.get('fiscalDateEnding', ''),
                        'reported_eps': q.get('reportedEPS', 'N/A'),
                        'estimated_eps': q.get('estimatedEPS', 'N/A'),
                        'surprise': q.get('surprise', 'N/A'),
                        'surprise_percentage': q.get('surprisePercentage', 'N/A')
                    }
                    for q in quarterly
                ],
                'annual_earnings': [
                    {
                        'fiscal_date_ending': a.get('fiscalDateEnding', ''),
                        'reported_eps': a.get('reportedEPS', 'N/A')
                    }
                    for a in annual
                ]
            }
        except Exception as e:
            print(f"Error fetching earnings: {e}")
            return {'symbol': symbol, 'quarterly_earnings': [], 'annual_earnings': []}

    def get_market_sentiment_summary(self, symbol: str) -> str:
        """
        Get a human-readable summary of market sentiment.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            String summary of sentiment analysis
        """
        news_data = self.get_news_sentiment(symbol)
        
        if news_data['articles_analyzed'] == 0:
            return f"No recent sentiment data available for {symbol}."
        
        avg_score = news_data['average_sentiment_score']
        dist = news_data['sentiment_distribution']
        
        # Determine overall sentiment
        if avg_score > 0.15:
            overall = "Bullish"
        elif avg_score < -0.15:
            overall = "Bearish"
        else:
            overall = "Neutral"
        
        summary = f"""
Alpha Vantage Sentiment Analysis for {symbol}:
- Articles Analyzed: {news_data['articles_analyzed']}
- Average Sentiment Score: {avg_score:.4f}
- Overall Sentiment: {overall}

Sentiment Distribution:
- Bullish: {dist.get('Bullish', 0)} articles
- Somewhat Bullish: {dist.get('Somewhat-Bullish', 0)} articles
- Neutral: {dist.get('Neutral', 0)} articles
- Somewhat Bearish: {dist.get('Somewhat-Bearish', 0)} articles
- Bearish: {dist.get('Bearish', 0)} articles

Top Headlines:
"""
        
        for i, article in enumerate(news_data['articles'][:5], 1):
            summary += f"{i}. {article['title']} (Sentiment: {article['ticker_sentiment_label']})\n"
        
        return summary.strip()
