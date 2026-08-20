import logging
from typing import List, Dict, Any
from nltk.sentiment.vader import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class SentimentEngine:
    def __init__(self):
        # Fallback lexicon model is much faster on CPU
        self.vader = SentimentIntensityAnalyzer()
        
    def score_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Scores a batch of texts using VADER (much faster than FinBERT on CPU).
        """
        results = []
        for text in texts:
            vader_scores = self.vader.polarity_scores(text)
            vader_compound = vader_scores['compound']
            
            results.append({
                "score": vader_compound,
                "confidence": abs(vader_compound),
                "model_version": "vader_fast",
                "vader_fallback": vader_compound
            })
            
        return results
