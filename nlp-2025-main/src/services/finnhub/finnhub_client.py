import os
from datetime import datetime, timedelta
from typing import List, Dict

import finnhub
from dotenv import load_dotenv

load_dotenv()


class FinnhubClient:
    """
    Client for interacting with Finnhub API.
    
    Provides methods to fetch company news, market sentiment, and social sentiment.
    """

    def __init__(self):
        """Initialize Finnhub client with API key from environment."""
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY not found in environment variables")
        
        self.client = finnhub.Client(api_key=api_key)

    def get_company_news(
        self, 
        symbol: str, 
        days_back: int = 30
    ) -> List[Dict]:
        """
        Fetch company-specific news articles.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            days_back: Number of days to look back for news
            
        Returns:
            List of news articles with headline, summary, source, datetime
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        news = self.client.company_news(
            symbol,
            _from=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d')
        )
        
        formatted_news = []
        for article in news:
            formatted_news.append({
                'headline': article.get('headline', ''),
                'summary': article.get('summary', ''),
                'source': article.get('source', ''),
                'datetime': datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'url': article.get('url', ''),
                'sentiment': self._categorize_sentiment(article.get('sentiment', 0))
            })
        
        return formatted_news

    def get_market_news(
        self, 
        category: str = 'general',
        min_count: int = 20
    ) -> List[Dict]:
        """
        Fetch general market news.
        
        Args:
            category: News category ('general', 'forex', 'crypto', 'merger')
            min_count: Minimum number of articles to fetch
            
        Returns:
            List of market news articles
        """
        news = self.client.general_news(category, minid=0)
        
        formatted_news = []
        for article in news[:min_count]:
            formatted_news.append({
                'headline': article.get('headline', ''),
                'summary': article.get('summary', ''),
                'source': article.get('source', ''),
                'datetime': datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'url': article.get('url', ''),
                'category': article.get('category', '')
            })
        
        return formatted_news

    def get_social_sentiment(
        self, 
        symbol: str
    ) -> Dict:
        """
        Get aggregated social media sentiment for a stock.
        
        This includes Reddit and Twitter sentiment scores.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with sentiment metrics from social media
        """
        try:
            sentiment = self.client.stock_social_sentiment(symbol)
            
            if not sentiment or 'reddit' not in sentiment:
                return {
                    'reddit_sentiment': 0,
                    'twitter_sentiment': 0,
                    'reddit_mention': 0,
                    'twitter_mention': 0,
                    'overall_sentiment': 'neutral'
                }
            
            reddit_data = sentiment.get('reddit', [])
            twitter_data = sentiment.get('twitter', [])
            
            # Calculate average sentiment
            reddit_sentiment = sum(item.get('score', 0) for item in reddit_data) / len(reddit_data) if reddit_data else 0
            twitter_sentiment = sum(item.get('score', 0) for item in twitter_data) / len(twitter_data) if twitter_data else 0
            
            reddit_mentions = sum(item.get('mention', 0) for item in reddit_data)
            twitter_mentions = sum(item.get('mention', 0) for item in twitter_data)
            
            overall_score = (reddit_sentiment + twitter_sentiment) / 2
            
            return {
                'reddit_sentiment': round(reddit_sentiment, 3),
                'twitter_sentiment': round(twitter_sentiment, 3),
                'reddit_mention': reddit_mentions,
                'twitter_mention': twitter_mentions,
                'overall_sentiment': self._categorize_sentiment(overall_score),
                'overall_score': round(overall_score, 3)
            }
        except Exception as e:
            print(f"Social sentiment not available (likely free tier limitation): {e}")
            return {
                'reddit_sentiment': 0,
                'twitter_sentiment': 0,
                'reddit_mention': 0,
                'twitter_mention': 0,
                'overall_sentiment': 'not_available',
                'note': 'Social sentiment not available in free tier'
            }

    def get_recommendation_trends(
        self, 
        symbol: str
    ) -> Dict:
        """
        Get analyst recommendation trends.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with buy/hold/sell recommendations
        """
        try:
            recommendations = self.client.recommendation_trends(symbol)
            
            if not recommendations:
                return {
                    'strong_buy': 0,
                    'buy': 0,
                    'hold': 0,
                    'sell': 0,
                    'strong_sell': 0,
                    'period': 'N/A'
                }
            
            latest = recommendations[0]
            return {
                'strong_buy': latest.get('strongBuy', 0),
                'buy': latest.get('buy', 0),
                'hold': latest.get('hold', 0),
                'sell': latest.get('sell', 0),
                'strong_sell': latest.get('strongSell', 0),
                'period': latest.get('period', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
            return {
                'strong_buy': 0,
                'buy': 0,
                'hold': 0,
                'sell': 0,
                'strong_sell': 0,
                'period': 'N/A'
            }

    def get_company_profile(
        self, 
        symbol: str
    ) -> Dict:
        """
        Get company profile and basic information.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            profile = self.client.company_profile2(symbol=symbol)
            
            return {
                'name': profile.get('name', 'N/A'),
                'ticker': profile.get('ticker', symbol),
                'exchange': profile.get('exchange', 'N/A'),
                'industry': profile.get('finnhubIndustry', 'N/A'),
                'ipo': profile.get('ipo', 'N/A'),
                'market_cap': profile.get('marketCapitalization', 0),
                'shares_outstanding': profile.get('shareOutstanding', 0),
                'logo': profile.get('logo', ''),
                'phone': profile.get('phone', 'N/A'),
                'weburl': profile.get('weburl', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching company profile: {e}")
            return {'name': 'N/A', 'ticker': symbol}

    @staticmethod
    def _categorize_sentiment(score: float) -> str:
        """
        Categorize sentiment score into positive/neutral/negative.
        
        Args:
            score: Sentiment score (typically -1 to 1)
            
        Returns:
            String: 'positive', 'neutral', or 'negative'
        """
        if score > 0.15:
            return 'positive'
        elif score < -0.15:
            return 'negative'
        else:
            return 'neutral'
