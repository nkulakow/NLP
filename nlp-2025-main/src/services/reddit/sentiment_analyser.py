import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

torch.classes.__path__ = []


class SentimentAnalyser:
    """
    A class to analyse sentiment using a pre-trained model.
    This class uses the Hugging Face Transformers library to load a pre-trained
    sentiment analysis model and tokenizer. It provides a method to analyse the
    sentiment of a given text input.
    Attributes:
        tokenizer (AutoTokenizer): The tokenizer for the pre-trained model.
        model (AutoModelForSequenceClassification): The pre-trained sentiment analysis model.
        labels (list): List of sentiment labels.
    """

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
        )
        self.labels = ["negative", "neutral", "positive"]

    def analyse(self, text: str) -> str:
        """
        Analyses the sentiment of the given text.
        Args:
            text (str): The input text to analyse.
        Returns:
            str: The sentiment label ('positive', 'neutral', 'negative').
        """
        if not text or text.strip() in ("[removed]", "[deleted]"):
            return "neutral"
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.inference_mode():
            outputs = self.model(**inputs)
        scores = outputs.logits.softmax(dim=1).numpy()[0]
        return self.labels[scores.argmax()]
