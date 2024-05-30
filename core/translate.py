from transformers import pipeline


class Translator:
    def __init__(self) -> None:
        self.pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
    
    def translate_to_en(self, text):
        """Translate the text in english and return the result"""
        return self.pipeline(text)[0]["translation_text"]