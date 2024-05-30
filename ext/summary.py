from discord.ext import commands, tasks
from util.summary import Summarizer  # noqa
from util.subject import Subjector
from util.chart import ChartHelper  # noqa
from core import Convolyzer  # noqa
from discord import File, app_commands
import discord
import sys


class SummaryCog(commands.Cog, name="Analyse de conversation"):
    """
    Voilà un kit d'outils qui te permettra de reprendre une conversation après une bonne journée de \
    travail, ou juste de mieux comprendre les différents aspects abordés. \
    Si tu n'es pas motivé, un petit résumé peut te simplifier la vie le soir, tu ne trouves pas ?
    """

    def __init__(self, bot: Convolyzer) -> None:
        # Setup utilities
        self.bot = bot
        self.summarizer = Summarizer(bot.pipeline_summary, bot.pipeline_topics)
        self.subjector = Subjector()

        self.sum_menu = app_commands.ContextMenu(
            name="Résumer à partir d'ici",
            callback=self.summary_all,
        )
        # Add context commands to the commands tree
        self.bot.tree.add_command(self.sum_menu)

        # Start timers
        self.updater.start()

    async def cog_unload(self) -> None:
        await self.subjector.close()
        self.updater.stop()

    # Timers ------------------------------------

    @tasks.loop(minutes=30)
    async def updater(self):
        await self.subjector.update()

    # Utilities ---------------------------------

    async def __fetch_messages(
        self, channel: discord.TextChannel, target_message: discord.Message = None
    ):
        messages = []
        prefix=self.bot.config.get_prefix()
        async for msg in channel.history(limit=100, after=target_message):
            if not msg.author.bot and not msg.content.startswith(prefix):
                t = (
                    msg.author.display_name,
                    msg.clean_content,
                    msg.created_at.timestamp(),
                    msg.id,
                )
                messages.append(t)
        return messages

    async def extract_topics(
        self, channel: discord.TextChannel, target_msg: discord.Message = None
    ):
        if target_msg:
            messages = await self.__fetch_messages(channel, target_msg)
            topics = await self.bot.run_in_thread(self.summarizer.topics, messages)
        else:
            messages = await self.__fetch_messages(channel)
            topics = await self.bot.run_in_thread(self.summarizer.topics_last, messages)
        return topics

    # Command context ---------------------------

    async def summary_all(
        self, interaction: discord.Interaction, target_message: discord.Message
    ) -> None:
        """Envoie le résumé à partir du message cible jusqu'au dernier message dans le canal"""
        # pls wait us discord 
        await interaction.response.defer(thinking=True)
        # fetch the messages
        messages = await self.__fetch_messages(interaction.channel, target_message)
        # get the topics
        topics = list((await self.extract_topics(interaction.channel)).items())
        if topics[0][1] - topics[0][1] <= 0.3:
            topic_text = f"Le thème de la discussion était {topics[0][0]} ou peut-être {topics[1][0]}."
        else:
            topic_text = (
                f"Le thème de la discussion précédente était: {topics[0][0]}"
            )
        # get the summary
        summary_all, list_users = await self.bot.run_in_thread(
            self.summarizer.summarize_all, messages
        )
        # Prepare the list of users as a formatted string
        user_lists_str = "\n".join([f"- {user}" for user in list_users])

        content = (
            f"*Voici mon beau résumé à partir de ce [message]({target_message.jump_url}) ! "
            "Les résumés ne sont ni repris ni échangés !*"
            "\n\n"
            f"{topic_text}"
            "\n\n"
            "**Qui a parlé ?**\n"
            f"{user_lists_str}"
            "\n\n"
            "**Mon beau résumé :**\n"
            f"{summary_all}"
        )

        await interaction.followup.send(content)

    # Commands ----------------------------------

    @commands.command(brief="Un petit résumé ?")
    async def summary(self, ctx: commands.Context):
        """
        Récupère la dernière conversation et rédige un petit résumé rien que pour toi ! \
        *C'est très addictif, attention >_<*.
        """
        await ctx.reply(
            "Je vais tenter de résumer la dernière conversation... J'espère qu'elle est intéressante !"
        )

        async with ctx.channel.typing():
            messages = await self.__fetch_messages(ctx.channel)
            # topics
            topics = list((await self.extract_topics(ctx.channel)).items())
            if topics[0][1] - topics[0][1] <= 0.3:
                topic_text = f"Le thème de la discussion était {topics[0][0]} ou peut-être {topics[1][0]}."
            else:
                topic_text = (
                    f"Le thème de la discussion précédente était: {topics[0][0]}"
                )

            # summary
            summary_last, list_users = await self.bot.run_in_thread(
                self.summarizer.summarize_last, messages
            )
            # Prepare the list of users as a formatted string
            user_lists_str = "\n".join([f"- {user}" for user in list_users])
            content = (
                "*Voici mon beau résumé ! Les résumés ne sont ni repris ni échangés !*"
                "\n\n"
                f"{topic_text}"
                "\n\n"
                "**Qui a parlé ?**\n"
                f"{user_lists_str}"
                "\n\n"
                "**Mon beau résumé :**\n"
                f"{summary_last}"
            )

            await ctx.reply(content)


async def setup(bot: commands.Bot):
    await bot.add_cog(SummaryCog(bot))


async def teardown(bot: commands.Bot):
    await bot.remove_cog("SummaryCog")
    del sys.modules["util.summary"]
