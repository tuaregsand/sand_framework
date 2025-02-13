import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from textblob import TextBlob
import json

logger = logging.getLogger(__name__)

class AnalyticsAgent:
    def __init__(self):
        self.price_api = "https://api.coingecko.com/api/v3/simple/price"
        self.twitter_bearer = os.getenv("TWITTER_BEARER_TOKEN")
        
        # Cache settings
        self.price_cache = {}
        self.price_cache_duration = timedelta(minutes=5)
        self.sentiment_cache = {}
        self.sentiment_cache_duration = timedelta(minutes=15)

    async def get_current_price(self) -> Dict[str, Union[float, str]]:
        """Get current Solana price in USD."""
        try:
            # Check cache first
            if self._is_price_cache_valid():
                return self.price_cache

            params = {
                "ids": "solana",
                "vs_currencies": "usd"
            }
            
            response = requests.get(
                self.price_api,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            price = data.get("solana", {}).get("usd")
            
            if not price:
                raise ValueError("Price data not found in response")
            
            result = {
                "price_usd": price,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update cache
            self.price_cache = result
            return result

        except Exception as e:
            logger.error(f"Error fetching price: {str(e)}")
            raise

    async def get_current_sentiment(self) -> Dict[str, Union[float, str]]:
        """Calculate current sentiment from social media."""
        try:
            # Check cache first
            if self._is_sentiment_cache_valid():
                return self.sentiment_cache

            # Fetch recent tweets
            tweets = await self._fetch_recent_tweets("solana", count=100)
            
            if not tweets:
                return {
                    "sentiment_score": 0.0,
                    "confidence": 0.0,
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Analyze sentiment
            sentiments = [
                self._analyze_sentiment(tweet["text"])
                for tweet in tweets
            ]
            
            # Calculate weighted average
            total_score = sum(s["score"] * s["confidence"] for s in sentiments)
            total_confidence = sum(s["confidence"] for s in sentiments)
            
            if total_confidence == 0:
                avg_sentiment = 0.0
            else:
                avg_sentiment = total_score / total_confidence

            result = {
                "sentiment_score": avg_sentiment,
                "confidence": total_confidence / len(sentiments),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update cache
            self.sentiment_cache = result
            return result

        except Exception as e:
            logger.error(f"Error calculating sentiment: {str(e)}")
            raise

    async def generate_alerts(self) -> List[Dict[str, str]]:
        """Generate alerts based on price and sentiment changes."""
        try:
            alerts = []
            
            # Get current price and sentiment
            price_data = await self.get_current_price()
            sentiment_data = await self.get_current_sentiment()
            
            # Check for significant price changes
            if self._is_price_change_significant(price_data["price_usd"]):
                alerts.append({
                    "type": "price_alert",
                    "message": f"Significant price movement detected: ${price_data['price_usd']:.2f}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # Check for significant sentiment changes
            if self._is_sentiment_change_significant(sentiment_data["sentiment_score"]):
                alerts.append({
                    "type": "sentiment_alert",
                    "message": f"Significant sentiment change detected: {sentiment_data['sentiment_score']:.2f}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return alerts

        except Exception as e:
            logger.error(f"Error generating alerts: {str(e)}")
            raise

    async def _fetch_recent_tweets(self, query: str, count: int = 100) -> List[Dict[str, str]]:
        """Fetch recent tweets about Solana."""
        if not self.twitter_bearer:
            logger.warning("Twitter bearer token not found")
            return []

        try:
            headers = {
                "Authorization": f"Bearer {self.twitter_bearer}"
            }
            
            params = {
                "query": f"{query} -is:retweet lang:en",
                "max_results": min(count, 100),
                "tweet.fields": "created_at,public_metrics"
            }
            
            response = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])

        except Exception as e:
            logger.error(f"Error fetching tweets: {str(e)}")
            return []

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using TextBlob."""
        try:
            analysis = TextBlob(text)
            
            # Get polarity (-1 to 1) and subjectivity (0 to 1)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            # Calculate confidence based on subjectivity
            # Higher subjectivity means we're more confident in the sentiment
            confidence = 0.3 + (0.7 * subjectivity)  # Scale from 0.3 to 1.0
            
            return {
                "score": polarity,
                "confidence": confidence
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"score": 0.0, "confidence": 0.0}

    def _is_price_cache_valid(self) -> bool:
        """Check if the price cache is still valid."""
        if not self.price_cache:
            return False
        
        cache_time = datetime.fromisoformat(self.price_cache["timestamp"])
        return datetime.utcnow() - cache_time < self.price_cache_duration

    def _is_sentiment_cache_valid(self) -> bool:
        """Check if the sentiment cache is still valid."""
        if not self.sentiment_cache:
            return False
        
        cache_time = datetime.fromisoformat(self.sentiment_cache["timestamp"])
        return datetime.utcnow() - cache_time < self.sentiment_cache_duration

    def _is_price_change_significant(self, current_price: float) -> bool:
        """Determine if a price change is significant enough for an alert."""
        try:
            # Load historical prices (placeholder - would typically load from database)
            # Consider price change significant if > 5% in last hour
            return False  # Placeholder
        except Exception:
            return False

    def _is_sentiment_change_significant(self, current_sentiment: float) -> bool:
        """Determine if a sentiment change is significant enough for an alert."""
        try:
            # Load historical sentiment (placeholder - would typically load from database)
            # Consider sentiment change significant if > 0.3 change in last hour
            return False  # Placeholder
        except Exception:
            return False
