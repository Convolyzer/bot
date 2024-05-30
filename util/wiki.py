import json
import aiohttp
import spacy
import random

class Wiki:

    def __init__(self):
        self.session = None  # To store aiohttp Session
        self.nlp = spacy.load("fr_core_news_md")
        self.initialize_session()  # Initialize session 

    def initialize_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def search(self, query):
        relevant_paragraphs = await self.__retrieve_relevant_paragraphs(query)  # Retrieve relevant paragraphs
        if relevant_paragraphs:
            result = relevant_paragraphs[0]
            # Check if the result is a disambiguation page or empty
            if "may refer to" in result or "NewPP limit report" in result or result == "":
                return None
            else:
                return result
        else:
            return None

    def extract_named_entities(self, text):
        doc = self.nlp(text)  # Process text with the loaded NLP model
        # Extract named entities of types PERSON, ORG, LOC, GPE
        named_entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "LOC", "GPE"]]
        return named_entities

    async def __retrieve_relevant_paragraphs(self, query):
        url = "https://fr.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exsentences": 5,  # Get the first 5 sentences of each paragraph
            "explaintext": 1,
            "titles": query,
            "lang": "fr"
        }

        async with self.session.get(url, params=params) as response:
            response_text = await response.text()
            data = json.loads(response_text)
            relevant_paragraphs = []
            if "pages" in data["query"]:
                for page_id, page_info in data["query"]["pages"].items():
                    if "extract" in page_info:
                        paragraphs = page_info["extract"].split("\n\n")  # Split paragraphs
                        print( paragraphs)
                        # Filter paragraphs containing the title
                        relevant_paragraphs = [p for p in paragraphs if query.lower() in p.lower() and p.endswith('.')]
                        # Randomly select a paragraph
                        random_paragraph = random.choice(relevant_paragraphs) if relevant_paragraphs else None
                        if random_paragraph:
                            # Get the first 3 lines of the paragraph
                            first_three_lines = '\n'.join(random_paragraph.split("\n")[:4])
                            return [first_three_lines]
            return []