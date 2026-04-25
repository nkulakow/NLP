import os
from datetime import datetime, timedelta, timezone

import praw
from dotenv import load_dotenv

load_dotenv()


class MockPost:
    def __init__(self, title, selftext):
        self.title = title
        self.selftext = selftext


class RedditClient:
    """
    A class to interact with Reddit API using PRAW (Python Reddit API Wrapper).

    Attributes:
        reddit (praw.Reddit): An instance of the Reddit API client.
    """

    def __init__(self):
        # self.reddit = praw.Reddit(
        #     client_id=os.getenv("REDDIT_CLIENT_ID"),
        #     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        #     user_agent=os.getenv("REDDIT_USER_AGENT"),
        # )
        pass

    def get_posts(self, subreddit: str, query: str, post_limit: int = 50, days: int = 30) -> list:
        """
        Fetches posts from a specific subreddit based on a query.
        Args:
            subreddit (str): The name of the subreddit to search in.
            query (str): The search query (e.g., stock symbol).
            post_limit (int): Maximum number of posts to fetch.
            days (int): Time window (in days) to look back for posts.
        Returns:
            list: A list of Reddit posts matching the query.
        """
        # sub = self.reddit.subreddit(subreddit)
        # start_date = datetime.now(timezone.utc) - timedelta(days=days)
        post1 = MockPost(
            "Strong Q3 2024 Financial Results for AAPL",
            "Apple just reported its Q3 2024 earnings. Revenue hit $93.3B USD, with EPS of $2.18 USD, "
            "beating analyst expectations. Gross margin came in at 46%, indicating a well-diversified product base. "
            "However, I'm noticing a 4% YoY decline in iPhone sales. I think this is due to increased competition in the smartphone market. "
            "The company's services segment is growing strong at 16% YoY, which is a bright spot."
        )
        post2 = MockPost(
            "AAPL: EU Regulatory Headwinds Could Impact Margins",
            "New EU regulations on digital markets interoperability could significantly pressure Apple's profit margins. "
            "Under the Digital Markets Act, Apple will be forced to allow app installations from third-party sources outside the App Store. "
            "This threatens the closed ecosystem model that's been central to their business strategy. "
            "I'm expecting a 5-10% stock price decline if these regulations are implemented without major concessions. "
            "Watch for any lobbying efforts or appeals from Apple."
        )
        post3 = MockPost(
            "AAPL Technical Analysis - Head & Shoulders Pattern Forming",
            "AAPL is currently trading at $228. I see a classic head-and-shoulders pattern forming on the daily chart. "
            "Key resistance levels: $235 (local high), $240 (previous resistance). Support at $220. "
            "If we break above $240, we could see a rally to $250 and potentially $260. However, the near-term bias looks bearish. "
            "The 50-day moving average is around $225, acting as intermediate support. RSI is at 65, suggesting some overbought conditions."
        )
        post4 = MockPost(
            "Apple Vision Pro: Revolutionary Tech or Overpriced Gadget?",
            "The newly released Apple Vision Pro has incredible technology, but the $3,500 price tag severely limits the addressable market. "
            "I see interest from tech enthusiasts, but mainstream consumers won't bite at this price point. "
            "The real growth catalyst will come when the price drops below $1,500 in 2-3 years. "
            "In the near term (next 2-3 quarters), this won't meaningfully impact revenue or stock price. "
            "But long-term, spatial computing could be as transformative as the iPhone was."
        )
        posts = [post1, post2, post3, post4]

        # for post in sub.search(query, sort="new", time_filter="all", limit=post_limit):
        #     post_date = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        #     if post_date >= start_date:
        #         posts.append(post)
        return posts
