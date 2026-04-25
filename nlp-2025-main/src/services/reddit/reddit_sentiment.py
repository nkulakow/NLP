from src.services.reddit.reddit_client import RedditClient
from src.services.reddit.sentiment_analyser import SentimentAnalyser


class RedditSentimentAnalyser:
    """
    A class to analyse Reddit sentiment for a given stock across multiple subreddits.

    Attributes:
        reddit_client (RedditClient): An instance of the RedditClient to fetch posts.
        sentiment_analyser (SentimentAnalyser): An instance of the SentimentAnalyser to analyse sentiment.
    """

    def __init__(self):
        self.reddit_client = RedditClient()
        self.sentiment_analyser = SentimentAnalyser()

    def analyse(self, subreddits: list, stock: str, post_limit: int = 50, days: int = 30) -> dict:
        """
        Analyses Reddit sentiment for a given stock across multiple subreddits.
        Args:
            subreddits (list): A list of subreddit names (e.g., ['stocks', 'investing']).
            stock (str): The stock ticker or keyword to search for (e.g., 'AAPL').
            post_limit (int): Maximum number of posts to analyse per subreddit.
            days (int): Time window (in days) to look back for Reddit posts.
        Returns:
            dict: A count of 'positive', 'neutral', and 'negative' sentiment results.
        """
        sentiment_counts = {"neutral": 0, "negative": 0, "positive": 0}
        for subreddit in subreddits:
            posts = self.reddit_client.get_posts(subreddit, stock, post_limit, days)
            for post in posts:
                text = f"{post.title}\n{post.selftext}"
                sentiment = self.sentiment_analyser.analyse(text)
                sentiment_counts[sentiment] += 1
        return sentiment_counts
