from typing import Dict, List

from src.services.finnhub.finnhub_client import FinnhubClient


class FinnhubSentimentAnalyser:
    """
    Analyzes sentiment using Finnhub API data sources.
    
    Combines company news sentiment, social media sentiment (Reddit/Twitter),
    and analyst recommendations to provide comprehensive sentiment analysis.
    """

    def __init__(self):
        """Initialize with Finnhub client."""
        self.client = FinnhubClient()

    def analyse(
        self, 
        symbol: str, 
        days_back: int = 30,
        news_count: int = 50
    ) -> Dict:
        """
        Perform comprehensive sentiment analysis for a stock.
        
        Args:
            symbol: Stock ticker symbol
            days_back: Number of days to look back for news
            news_count: Number of news articles to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Fetch data from multiple sources
        company_news = self.client.get_company_news(symbol, days_back)[:news_count]
        social_sentiment = self.client.get_social_sentiment(symbol)
        recommendations = self.client.get_recommendation_trends(symbol)
        
        # Analyze news sentiment
        news_sentiment = self._analyze_news_sentiment(company_news)
        
        # Calculate overall sentiment
        overall_sentiment = self._calculate_overall_sentiment(
            news_sentiment,
            social_sentiment,
            recommendations
        )
        
        return {
            'symbol': symbol,
            'analysis_period_days': days_back,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'analyst_recommendations': recommendations,
            'overall_sentiment': overall_sentiment,
            'summary': self._generate_summary(
                news_sentiment,
                social_sentiment,
                recommendations,
                overall_sentiment
            )
        }

    def _analyze_news_sentiment(self, news_articles: List[Dict]) -> Dict:
        """
        Analyze sentiment from news articles.
        
        Args:
            news_articles: List of news article dictionaries
            
        Returns:
            Dictionary with news sentiment metrics
        """
        if not news_articles:
            return {
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'total_articles': 0,
                'sentiment_score': 0,
                'dominant_sentiment': 'neutral'
            }
        
        sentiment_counts = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        
        for article in news_articles:
            sentiment = article.get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1
        
        total = len(news_articles)
        sentiment_score = (
            sentiment_counts['positive'] - sentiment_counts['negative']
        ) / total if total > 0 else 0
        
        dominant = max(sentiment_counts, key=sentiment_counts.get)
        
        return {
            'positive_count': sentiment_counts['positive'],
            'neutral_count': sentiment_counts['neutral'],
            'negative_count': sentiment_counts['negative'],
            'total_articles': total,
            'sentiment_score': round(sentiment_score, 3),
            'dominant_sentiment': dominant,
            'positive_percentage': round((sentiment_counts['positive'] / total) * 100, 1) if total > 0 else 0,
            'negative_percentage': round((sentiment_counts['negative'] / total) * 100, 1) if total > 0 else 0,
            'recent_headlines': [article['headline'] for article in news_articles[:5]]
        }

    def _calculate_overall_sentiment(
        self,
        news_sentiment: Dict,
        social_sentiment: Dict,
        recommendations: Dict
    ) -> Dict:
        """
        Calculate overall sentiment combining all sources.
        
        Weights:
        - News sentiment: 40%
        - Social sentiment: 30%
        - Analyst recommendations: 30%
        
        Args:
            news_sentiment: News sentiment data
            social_sentiment: Social media sentiment data
            recommendations: Analyst recommendations data
            
        Returns:
            Dictionary with overall sentiment metrics
        """
        # News sentiment score (-1 to 1)
        news_score = news_sentiment.get('sentiment_score', 0)
        
        # Social sentiment score (-1 to 1)
        social_score = social_sentiment.get('overall_score', 0)
        
        # Analyst recommendation score (-1 to 1)
        total_recommendations = (
            recommendations.get('strong_buy', 0) +
            recommendations.get('buy', 0) +
            recommendations.get('hold', 0) +
            recommendations.get('sell', 0) +
            recommendations.get('strong_sell', 0)
        )
        
        if total_recommendations > 0:
            recommendation_score = (
                (recommendations.get('strong_buy', 0) * 2 +
                 recommendations.get('buy', 0) * 1 +
                 recommendations.get('hold', 0) * 0 +
                 recommendations.get('sell', 0) * -1 +
                 recommendations.get('strong_sell', 0) * -2) / total_recommendations
            ) / 2  # Normalize to -1 to 1
        else:
            recommendation_score = 0
        
        # Weighted average
        weights = {'news': 0.4, 'social': 0.3, 'analyst': 0.3}
        overall_score = (
            news_score * weights['news'] +
            social_score * weights['social'] +
            recommendation_score * weights['analyst']
        )
        
        # Categorize
        if overall_score > 0.2:
            sentiment_label = 'Bullish'
        elif overall_score < -0.2:
            sentiment_label = 'Bearish'
        else:
            sentiment_label = 'Neutral'
        
        # Confidence level
        score_range = max(abs(news_score), abs(social_score), abs(recommendation_score))
        if score_range > 0.6:
            confidence = 'High'
        elif score_range > 0.3:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        return {
            'overall_score': round(overall_score, 3),
            'sentiment_label': sentiment_label,
            'confidence': confidence,
            'news_contribution': round(news_score * weights['news'], 3),
            'social_contribution': round(social_score * weights['social'], 3),
            'analyst_contribution': round(recommendation_score * weights['analyst'], 3)
        }

    def _generate_summary(
        self,
        news_sentiment: Dict,
        social_sentiment: Dict,
        recommendations: Dict,
        overall_sentiment: Dict
    ) -> str:
        """
        Generate human-readable summary of sentiment analysis.
        
        Args:
            news_sentiment: News sentiment data
            social_sentiment: Social media sentiment data
            recommendations: Analyst recommendations
            overall_sentiment: Overall sentiment metrics
            
        Returns:
            String summary
        """
        summary_parts = []
        
        # Overall sentiment
        summary_parts.append(
            f"Overall Market Sentiment: {overall_sentiment['sentiment_label']} "
            f"(Score: {overall_sentiment['overall_score']}, Confidence: {overall_sentiment['confidence']})"
        )
        
        # News sentiment
        news_total = news_sentiment['total_articles']
        news_dominant = news_sentiment['dominant_sentiment']
        summary_parts.append(
            f"\nNews Analysis ({news_total} articles): {news_dominant.capitalize()} sentiment dominates "
            f"({news_sentiment['positive_percentage']}% positive, "
            f"{news_sentiment['negative_percentage']}% negative)"
        )
        
        # Social sentiment
        reddit_score = social_sentiment['reddit_sentiment']
        twitter_score = social_sentiment['twitter_sentiment']
        summary_parts.append(
            f"\nSocial Media: Reddit sentiment {reddit_score:.2f}, "
            f"Twitter sentiment {twitter_score:.2f} "
            f"({social_sentiment['reddit_mention']} Reddit mentions, "
            f"{social_sentiment['twitter_mention']} Twitter mentions)"
        )
        
        # Analyst recommendations
        total_analysts = sum([
            recommendations.get('strong_buy', 0),
            recommendations.get('buy', 0),
            recommendations.get('hold', 0),
            recommendations.get('sell', 0),
            recommendations.get('strong_sell', 0)
        ])
        
        if total_analysts > 0:
            summary_parts.append(
                f"\nAnalyst Recommendations ({total_analysts} analysts): "
                f"{recommendations.get('strong_buy', 0)} Strong Buy, "
                f"{recommendations.get('buy', 0)} Buy, "
                f"{recommendations.get('hold', 0)} Hold, "
                f"{recommendations.get('sell', 0)} Sell, "
                f"{recommendations.get('strong_sell', 0)} Strong Sell"
            )
        
        return "".join(summary_parts)
