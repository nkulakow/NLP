import json

from crewai.tools import tool

from src.services.reddit.reddit_sentiment import RedditSentimentAnalyser

analyser = RedditSentimentAnalyser()


@tool
def analyse_reddit(subreddits: list, stock: str, post_limit=50, days=30) -> str:
    """
    Analyses Reddit sentiment for a given stock across multiple subreddits.

    Args:
        subreddits (list): A list of subreddit names (e.g., ['stocks', 'investing']).
        stock (str): The stock ticker or keyword to search for (e.g., 'AAPL').
        post_limit (int): Maximum number of posts to analyse per subreddit.
        days (int): Time window (in days) to look back for Reddit posts.

    Returns:
        str: A JSON string containing the count of 'positive', 'neutral', and 'negative' sentiment results.
    """
    sentiments = analyser.analyse(subreddits, stock, post_limit, days)
    return json.dumps(sentiments, indent=2)
