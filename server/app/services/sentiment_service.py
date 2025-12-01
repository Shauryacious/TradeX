"""
Sentiment Analysis Service
Uses VADER and transformers for sentiment analysis
"""

from typing import Dict, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import SentimentAnalysisError

logger = setup_logging()


class SentimentService:
    """Service for analyzing tweet sentiment"""
    
    def __init__(self):
        """Initialize sentiment analyzers"""
        try:
            # VADER - fast and good for social media
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            # Transformer-based model for more accurate analysis
            # Using a lightweight model for production
            self.transformer_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1,  # Use CPU by default
            )
            logger.info("Sentiment analyzers initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzers: {e}")
            raise SentimentAnalysisError(f"Sentiment analyzer initialization failed: {e}")
    
    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores and label
        """
        try:
            # VADER analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            vader_compound = vader_scores["compound"]
            
            # Transformer analysis
            transformer_result = self.transformer_analyzer(text)[0]
            transformer_label = transformer_result["label"].lower()
            transformer_score = transformer_result["score"]
            
            # Map transformer labels to scores
            if "positive" in transformer_label:
                transformer_sentiment = transformer_score
            elif "negative" in transformer_label:
                transformer_sentiment = -transformer_score
            else:  # neutral
                transformer_sentiment = 0.0
            
            # Weighted combination (VADER is good for social media, transformer for accuracy)
            combined_score = (vader_compound * 0.4) + (transformer_sentiment * 0.6)
            
            # Determine label
            if combined_score >= settings.SENTIMENT_THRESHOLD_POSITIVE:
                label = "positive"
            elif combined_score <= settings.SENTIMENT_THRESHOLD_NEGATIVE:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                "score": round(combined_score, 4),
                "label": label,
                "vader_score": round(vader_compound, 4),
                "transformer_score": round(transformer_sentiment, 4),
                "confidence": round(transformer_score, 4),
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise SentimentAnalysisError(f"Sentiment analysis error: {e}")

