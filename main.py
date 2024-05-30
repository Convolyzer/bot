import discord
import os
import matplotlib

from core.config import Config
from core.bot import Convolyzer

import spacy
from spacy.cli.download import download as spacy_download
# Change matplotlib backend
matplotlib.use('agg')


# Load the config
config = Config("config.json")

# Create the data directory
os.makedirs("data", exist_ok=True)
os.makedirs("data/graph", exist_ok=True)

# Setup Discord intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True

# Install spacy
def load_spacy_model():
        try:
            nlp = spacy.load("fr_core_news_md")
        except OSError:
            print("Language model not found. Downloading...")
            spacy_download("fr_core_news_md")
load_spacy_model()

# Setup the bot
bot = Convolyzer(config.get_prefix(), intents, config)

# Run the bot
bot.run(config.get_token())
