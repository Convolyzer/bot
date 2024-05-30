from discord.ext import commands
from util.wiki import Wiki
import time
import discord

class DiscoverCog(commands.Cog, name="Découverte"):
    """
    C'est important de découvrir des choses, mais ça l'est encore plus à plusieurs ! \
    Voilà de quoi t'amuser et améliorer tes conversations avec tes amis facilement.
    De petits points de culture vont s'afficher en fonction de tes discussions !
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.wiki = Wiki()
        self.last_search_times = {}  # Dictionary to store last search time for each guild
        self.search_cooldown = 15  # Default cooldown time
    
    async def cog_unload(self) -> None:
        await self.wiki.close_session()
    
    # Events ------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return
        else:
            guild_id = message.guild.id
            # Check if enough time has passed since the last search for this guild
            if guild_id not in self.last_search_times or (time.time() - self.last_search_times[guild_id]) > self.search_cooldown:
                # Process the clean message using SpaCy NER
                named_entities = self.wiki.extract_named_entities(message.content)
                if named_entities:
                    wikipedia = await self.wiki.search(named_entities[0])
                    if wikipedia:
                        await message.channel.send("Sais-tu que :\n" + wikipedia)
                        # Update the last search time for this guild
                        self.last_search_times[guild_id] = time.time()
            else:
                # Ignore the message if the cooldown period has not passed
                return
    
    # Commands ----------------------------------

    @commands.command(brief="Envoie des infos sur *quelque chose*.")
    async def wiki(self, ctx, *, query):
        """
        Entre un mot-clé, un truc qui te passe par la tête, tout ce que tu veux ! \
        Peut-être que je te trouverai une petite info sympa dessus >_<.
        """
        # Searching Wikipedia for the query
        wikipedia = await self.wiki.search(query)

        # If a result is found, send it to the user
        if wikipedia is not None:
            await ctx.reply(wikipedia + ".")
        # If no result is found, prompt the user to be more specific or change the query
        else:
            await ctx.reply("Sois plus précis ou change le mot s'il te plaît :pray:.")

    
    @commands.command(brief="Envoie un sujet de conversation.")
    async def subject(self, ctx: commands.Context):
        """
        La conversation touche à sa fin, c'est ennuyeux ? Alors j'ai la solution ! \
        Cette commande va envoyer un sujet de conversation en lien avec la discussion précédente. \
        Je suis sûr que vous allez en parler des jours...
        """
        summary_cog = self.bot.get_cog_by_class_name("SummaryCog")
        if not summary_cog:
            await ctx.reply("Cette commande n'est pas disponnible pour le moment, désolé !")
            return
        subjector = summary_cog.subjector
        # get topics
        topics = await summary_cog.extract_topics(ctx.channel)
        topic = list(topics.keys())[0]
        # get a subject on this topic
        entry = subjector.get_random_entry(topic)
        if not entry:
            await ctx.reply("Aucun sujet trouvé... :sob:")
            return
        # create a beautiful embed
        color = discord.Color.from_str(self.bot.config.get_color())
        embed = discord.Embed(
            title=entry.title,
            url=entry.link,
            color=color,
            description=entry.description,
        )
        embed.set_footer(text=f"Publié le {entry.published} !")
        # send the subject
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(DiscoverCog(bot))

async def teardown(bot: commands.Bot):
    await bot.remove_cog("DiscoverCog")
