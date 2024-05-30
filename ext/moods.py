import asyncio
import random
import sys

import discord
from discord.ext import commands, tasks
from discord import Guild, File, Member, Interaction, app_commands, Message
from datetime import datetime
from typing import List

from core import Convolyzer
from util.mbti import GuildMBTI
from util.moods import GuildMoods
from util.chart import ChartHelper
from util.ascii import AsciiHelper


class MoodsCog(commands.Cog, name="Émotions et personnalités"):
    """
    Tu trouves ça difficile de comprendre les gens ? Moi aussi ! \
    Dans ce module, tu trouveras tous mes outils que j'ai développés pour t'aider ! \
    Amuse-toi bien à analyser tes amis, mais ne les utilise pas pour faire du mal ! \
    Sinon, je viendrai te chercher... >_<.
    """

    MBTI_COMPATIBILITY = {
        "INFP": ("ENFP", "ENTJ"),
        "ENFP": ("INFJ", "INTJ"),
        "INFJ": ("ENFP", "ENTP"),
        "ENFJ": ("INFP", "ISFP"),
        "INTJ": ("ENFP", "ENTP"),
        "ENTJ": ("INFP", "INTP"),
        "INTP": ("ENTJ", "ESTJ"),
        "ENTP": ("INFP", "INTJ"),
        "ISFP": ("ENFJ", "ESFJ", "ESTJ"),
        "ESFP": ("ISFJ", "ISTJ"),
        "ISTP": ("ESFJ", "ESTJ"),
        "ESTP": ("ISFJ", "ISTJ"),
        "ISFJ": ("ESFP", "ESTP"),
        "ESFJ": ("ISFP", "ISTP"),
        "ISTJ": ("ESFP", "ESTP"),
        "ESTJ": ("INTP", "ISFP", "ISTP"),
    }

    def __init__(self, bot: Convolyzer) -> None:
        """
        Initializes the MoodsCog class.

        Args:
            bot (Convolyzer): The instance of the Convolyzer bot.
        """
        self.bot = bot
        self.__guild_mood_map = {}  # Type: dict[int, GuildMoods]
        self.__guild_mbti_map = {}  # Type: dict[int, GuildMBTI]
        self.ascii_helper = AsciiHelper()  # Type: AsciiHelper
        self.chart_helper = ChartHelper()  # Type: ChartHelper
        self.ctx_menu_mbti = app_commands.ContextMenu(
            name="Affiche le type MBTI", callback=self.mbti_from_message
        )
        self.ctx_menu_mood = app_commands.ContextMenu(
            name="Affiche l'émotion", callback=self.mood_from_message
        )
        self.ctx_menu_sentiment = app_commands.ContextMenu(
            name="Affiche les sentiments", callback=self.sentiment_from_message
        )
        self.bot.tree.add_command(self.ctx_menu_mbti)
        self.bot.tree.add_command(self.ctx_menu_mood)
        self.bot.tree.add_command(self.ctx_menu_sentiment)
        self.mood_colors = {
            "amour": "lightpink",
            "joie": "gold",
            "surprise": "lightgreen",
            "colère": "orangered",
            "tristesse": "skyblue",
            "peur": "red",
            "Autres": "gray",
        }
        self.pov_colors = {
            "Subjectif": "turquoise",
            "Objectif": "violet",
            "Autres": "gray",
        }
        self.positivity_colors = {
            "Positif": "green",
            "Negatif": "mediumorchid",
            "Autres": "gray",
        }
        self.mbti_colors = {
            "ISTJ": "blue",
            "ISFJ": "green",
            "INFJ": "purple",
            "INTJ": "black",
            "ISTP": "gray",
            "ISFP": "brown",
            "INFP": "teal",
            "INTP": "midnightblue",
            "ESTP": "orange",
            "ESFP": "yellow",
            "ENFP": "pink",
            "ENTP": "darkkhaki",
            "ESTJ": "darkred",
            "ESFJ": "deeppink",
            "ENFJ": "silver",
            "ENTJ": "darkgreen",
        }

    async def cog_unload(self) -> None:
        """
        Unloads the cog by removing the context menu commands from the bot's command tree.
        """
        self.bot.tree.remove_command(
            self.ctx_menu_mbti.name, type=self.ctx_menu_mbti.type
        )
        self.bot.tree.remove_command(
            self.ctx_menu_mood.name, type=self.ctx_menu_mood.type
        )
        self.bot.tree.remove_command(
            self.ctx_menu_sentiment.name, type=self.ctx_menu_sentiment.type
        )

    # Utilities ---------------------------------

    def get_guild_moods(self, guild: Guild) -> GuildMoods:
        """
        Retrieves or initializes the GuildMoods instance for the given guild.

        Args:
            guild (Guild): The guild to retrieve or initialize GuildMoods for.

        Returns:
            GuildMoods: The GuildMoods instance for the given guild.
        """
        guild_id = guild.id
        if guild_id in self.__guild_mood_map:
            return self.__guild_mood_map[guild_id]

        pipeline_mood = self.bot.pipeline_mood
        pipeline_positivity = self.bot.pipeline_sentiment
        guild_moods = GuildMoods(pipeline_mood, pipeline_positivity)
        self.__guild_mood_map[guild_id] = guild_moods
        return guild_moods

    def get_guild_mbti(self, guild: Guild) -> GuildMBTI:
        """
        Retrieves or initializes the GuildMBTI instance for the given guild.

        Args:
            guild (Guild): The guild to retrieve or initialize GuildMBTI for.

        Returns:
            GuildMBTI: The GuildMBTI instance for the given guild.
        """
        guild_id = guild.id
        if guild_id in self.__guild_mbti_map:
            return self.__guild_mbti_map[guild_id]

        pipeline_mbti = self.bot.pipeline_mbti
        translator = self.bot.translator
        guild_mbti = GuildMBTI(pipeline_mbti, translator)
        self.__guild_mbti_map[guild_id] = guild_mbti
        return guild_mbti

    def get_compatible_members(
        self, guild: discord.Guild, member: discord.User
    ) -> List[discord.Member]:
        C_MOOD = 0.2
        C_POV = 0.2
        C_POS = 0.3
        C_MBTI = 0.2
        C_ASCII = 0.1

        members = [m for m in guild.members if m != member and not m.bot]
        res = []

        max_mood = lambda d: None if not d else list(d.keys())[0]

        guild_mbti = self.get_guild_mbti(guild)
        guild_moods = self.get_guild_moods(guild)

        member_mood = max_mood(guild_moods.get_user_mood(member.id))
        member_pov = guild_moods.get_user_pov(member.id)
        member_positivities = guild_moods.get_user_positivity(member.id)
        member_mbti = guild_mbti.get_user_mbti(member.id)
        compatible = self.MBTI_COMPATIBILITY.get(member_mbti, [])

        for member_bis in members:
            score = 0
            # moods score
            if max_mood(guild_moods.get_user_mood(member_bis.id)) == member_mood:
                tmp_score = 1
            else:
                tmp_score = 0.5
            score += tmp_score * C_MOOD
            # pov
            tmp_score = 1 - abs(guild_moods.get_user_pov(member_bis.id) - member_pov)
            score += tmp_score * C_POV
            # positivities
            tmp_score = 1 - abs(
                guild_moods.get_user_positivity(member_bis.id) - member_positivities
            )
            score += tmp_score * C_POS
            # mbti score
            if guild_mbti.get_user_mbti(member_bis.id) in compatible:
                tmp_score = 1
            else:
                tmp_score = 0.5
            score += tmp_score * C_MBTI
            # ascii because the username say a lot about you!
            member_ascii = [ord(l) for l in member.name]
            member_sum = sum(member_ascii)

            member_bis_ascii = [ord(l) for l in member_bis.name]
            member_bis_sum = sum(member_bis_ascii)

            if min(member_sum, member_bis_sum) == member_sum:
                tmp_score = member_sum / member_bis_sum
            else:
                tmp_score = member_bis_sum / member_sum
            score += tmp_score * C_ASCII

            # normalize
            score /= C_MOOD + C_POV + C_POS + C_MBTI + C_ASCII
            res.append((member_bis, score))

        # sort members
        res = sorted(res, key=lambda e: e[1], reverse=True)

        # ready!
        return res

    # Timers ------------------------------------

    @tasks.loop(minutes=10)
    async def cleaner(self):
        """
        Periodically cleans mood data for all guilds by invoking the garbage collector.
        """
        futures = []
        for guild in self.__guild_mood_map.values():
            futures.append(self.bot.run_in_thread(guild.garbage_collector))
        await asyncio.gather(*futures)

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """
        Handles the on_message event and processes the message for mood and MBTI classification.

        Args:
            message (Message): The message sent by a user.
        """
        if message.author.bot:
            return

        if not self.bot.auth_manager.is_allowed(message.author.id):
            return

        # List of special characters
        special_characters = "!@#$%^&*()-_+=[]{}|;:',.<>?"

        # Check if the message starts with any special character
        if message.content.startswith(tuple(special_characters)):
            return

        guild = message.guild
        if guild:
            moods_instance = self.get_guild_moods(guild)
            mbti_instance = self.get_guild_mbti(guild)

            await self.bot.run_in_thread(
                moods_instance.handle_message,
                message.author.id,
                message.content,
                message.id,
                datetime.now(),
            )
            await self.bot.run_in_thread(
                mbti_instance.handle_message, message.author.id, message.content
            )

    # Commands ----------------------------------

    @commands.command(brief="Affiche les émotions d'un membre.")
    async def mood(self, ctx: commands.Context, member: Member = None):
        """
        Tu veux savoir ce que toi ou un membre ressentez au plus profond de vous ? \
        Cette commande va afficher des la distribution de vos émotions dans un beau graphique ! \
        Evidement, le resultat est très précis !
        """
        member = member or ctx.author

        mood_instance = self.get_guild_moods(ctx.guild)

        mood_data = mood_instance.get_user_mood(member.id)

        if not mood_data:
            no_data = f"Données moods non disponibles pour {member.mention} :sob:."
            await ctx.reply(no_data)
            return

        fun_titres = [
            "La folie des moods de {member.display_name}",
            "Les émotions en folie chez {member.display_name}",
            "Le grand spectacle des humeurs de {member.display_name}",
            "Moods à gogo : La saga de {member.display_name}",
            "Le défilé des humeurs de {member.display_name}",
            "Humeurs et gribouillis : Le show de {member.display_name}",
            "Moods Mania : L'édition spéciale de {member.display_name}",
            "Le carnaval des émotions chez {member.display_name}",
        ]

        titre = random.choice(fun_titres).format(member=member)

        mood_colors = [self.mood_colors.get(label) for label in mood_data.keys()]

        chart_image = self.chart_helper.create_pie_chart(
            mood_data, title=titre, colors=mood_colors
        )

        await ctx.reply(file=File(chart_image, "mood_chart.png"))

    @commands.command(brief="Affiche les émotions de tous les membres.")
    async def moods(self, ctx: commands.Context):
        """
        Un petit outils pour voir comment se porte ton serveur... \
        Si tous le monde va mal, il faudrait peut-être contacter les modérateurs, non ?
        """
        moods_instance = self.get_guild_moods(ctx.guild)

        mood_data = moods_instance.get_guild_mood()

        mood_data_filtered = {
            label: value for label, value in mood_data.items() if value != 0
        }

        if not mood_data_filtered:
            no_data = f"Données moods non disponibles pour **{ctx.guild.name}** :sob:."
            await ctx.reply(no_data)
            return

        fun_titres = [
            "La folie des moods sur {guild_name}",
            "Les émotions en folie chez les membres de {guild_name}",
            "Le grand spectacle des humeurs sur {guild_name}",
            "Moods à gogo : La saga de {guild_name}",
            "Le défilé des humeurs sur {guild_name}",
            "Humeurs et gribouillis : Le show sur {guild_name}",
            "Moods Mania : L'édition spéciale de {guild_name}",
            "Le carnaval des émotions sur {guild_name}",
        ]

        titres = random.choice(fun_titres).format(guild_name=ctx.guild.name)

        mood_colors = [
            self.mood_colors.get(label) for label in mood_data_filtered.keys()
        ]

        chart_image = self.chart_helper.create_pie_chart(
            mood_data_filtered, title=titres, colors=mood_colors
        )

        await ctx.reply(file=File(chart_image, "moods_chart.png"))

    @commands.command(brief="Affiche le point de vue d'un membre.")
    async def pov(self, ctx: commands.Context, member: Member = None) -> None:
        """
        Tu as un doute sur toi ou un membre en plein débat ? Alors utilise cette commande ! \
        Tu pourras directement voir si toi ou le membre est subjectif ou objectif. C'est cool, non ?
        """
        member = member or ctx.author

        guild_moods = self.get_guild_moods(ctx.guild)

        pov_score = guild_moods.get_user_pov(member.id)

        progress_bar = self.ascii_helper.get_progress_bar(pov_score)

        fun_titres_pov = [
            "La subjectivité de {member.display_name} : Quel pourcentage de subjectivité ? ",
            "Quelle est la part de subjectivité chez {member.display_name} ? ",
            "La subjectivité de {member.display_name} : Mystère et spéculations ",
            "La subjectivité de {member.display_name} : La quête du pourcentage ultime ",
            "Le score de subjectivité de {member.display_name} : Un voyage subjectif ",
            "Quel est le niveau de subjectivité chez {member.display_name} ? ",
        ]

        pov_message = random.choice(fun_titres_pov).format(member=member)

        await ctx.reply(f"{pov_message}{progress_bar}")

    @commands.command(brief="Affiche le points de vue de tous les membres du serveur.")
    async def povs(self, ctx: commands.Context) -> None:
        """
        Une petite vision globale du point de vue des membres du serveur. \
        Je te conseille de vérifier ça avant de parler d'un truc vraiment sérieux !
        """
        guild_moods = self.get_guild_moods(ctx.guild)

        pov_data = guild_moods.get_guild_pov()

        if not pov_data:
            no_data = (
                f"Données subjectivité non disponibles pour **{ctx.guild.name}** :sob:."
            )
            await ctx.reply(no_data)
            return

        fun_titres_povs = [
            "La guerre de la subjectivité et de l'objectivité sur {guild_name}",
            "Les deux visages de la subjectivité sur {guild_name}",
            "Subjectivité vs Objectivité : Le duel sur {guild_name}",
            "Les extrêmes se rencontrent : Subjectivité et Objectivité sur {guild_name}",
            "La subjectivité et l'objectivité : Un match épique sur {guild_name}",
        ]

        titre = random.choice(fun_titres_povs).format(guild_name=ctx.guild.name)

        pov_colors = [self.pov_colors.get(label) for label in pov_data.keys()]

        chart_image = self.chart_helper.create_pie_chart(
            pov_data, title=titre, colors=pov_colors
        )

        await ctx.reply(file=File(chart_image, "pov_chart.png"))

    @commands.command(brief="Affiche la positivité d'un membre.")
    async def positivity(self, ctx: commands.Context, member: Member = None) -> None:
        """
        Un moyen simple de savoir si toi ou un membre est positif ou négatif. \
        Pourquoi ne pas aller réconforter les gens négatifs ? Tu pourrais te faire de nouveaux amis !
        """
        member = member or ctx.author

        guild_moods = self.get_guild_moods(ctx.guild)

        positivity_score = guild_moods.get_user_positivity(member.id)

        progress_bar = self.ascii_helper.get_progress_bar(positivity_score)

        positivity_message = [
            "La positivité de {member.display_name} : Quel pourcentage de bonheur ? ",
            "Quelle est la part de positivité chez {member.display_name} ? ",
            "La positivité de {member.display_name} : Mystère et joie ",
            "La positivité de {member.display_name} : La quête du pourcentage ultime ",
            "Le score de positivité de {member.display_name} : Un voyage joyeux ",
            "Quel est le niveau de positivité chez {member.display_name} ? ",
        ]

        titre = random.choice(positivity_message).format(member=member)

        await ctx.reply(f"{titre}{progress_bar}")

    @commands.command(brief="Affiche la positivité de tous les membres.")
    async def positivities(self, ctx: commands.Context) -> None:
        """
        Envie de voir comment va ton serveur ? Je ne suis pas responsable d'un triste constat, on est d'accord ? >_<
        Essayer d'avoir tous les membres positifs pourrait être un bon moyen pour rendre le serveur plus attractif, tu ne trouves pas ?
        """
        guild_moods = self.get_guild_moods(ctx.guild)

        positivity_data = guild_moods.get_guild_positivity()

        if not positivity_data:
            no_data = (
                f"Données positivité non disponibles pour **{ctx.guild.name}** :sob:."
            )
            await ctx.reply(no_data)
            return

        fun_titres_positivities = [
            "Le combat de la positivité et de la négativité sur {guild_name}",
            "Les deux visages de la positivité sur {guild_name}",
            "Positivité vs Négativité : Le duel sur {guild_name}",
            "Les extrêmes se rencontrent : Positivité et négativité sur {guild_name}",
            "La positivité et la négativité : Un match lumineux sur {guild_name}",
        ]
        titre = random.choice(fun_titres_positivities).format(guild_name=ctx.guild.name)

        positivity_colors = [
            self.positivity_colors.get(label) for label in positivity_data.keys()
        ]

        chart_image = self.chart_helper.create_pie_chart(
            positivity_data, title=titre, colors=positivity_colors
        )

        await ctx.reply(file=File(chart_image, "positivity_chart.png"))

    @commands.command(brief="Affiche le type MBTI d'un membre.")
    async def mbti(self, ctx: commands.Context, member: Member = None) -> None:
        """
        Tu veux connaître ton type MBTI ou celui d'un autre membre ? Alors, tu es au bon endroit ! \
        Le type MBTI permet aux gens d'en savoir un peu plus sur toi, ton comportement, etc. \
        C'est un bon moyen pour tenter une approche avec une nouvelle personne !
        """
        member = member or ctx.author

        guild_mbti = self.get_guild_mbti(ctx.guild)

        mbti_type = guild_mbti.get_user_mbti(member.id)

        if mbti_type:
            mbti_url = f"https://www.16personalities.com/fr/la-personnalite-{mbti_type.lower()}"
            await ctx.reply(
                f"Le type MBTI dominant pour {member.mention} est : **{mbti_type}** :tada:\n"
                f":mag: Voici plus d'infos sur ce type : {mbti_url} :eyes:"
            )
        else:
            await ctx.reply(
                f"Données MBTI non disponibles pour {member.mention} :sob:."
            )

    @commands.command(brief="Affiche les types MBTI des membres.")
    async def mbtis(self, ctx: commands.Context):
        """
        Envie de voir si tu vas bien t'entendre avec les membres de ce serveur ? \
        Tu peux vérifier en un coup d'œil quel type est le plus présent au sein de la communauté.
        """
        mbti_instance = self.get_guild_mbti(ctx.guild)

        mbti_data = mbti_instance.get_guild_mbtis()

        if not mbti_data:
            no_data = f"Données MBTI non disponibles pour **{ctx.guild.name}** :sob:."
            await ctx.reply(no_data)
            return

        mbti_colors = [self.mbti_colors.get(label) for label in mbti_data.keys()]

        chart_image = self.chart_helper.create_pie_chart(
            mbti_data,
            title=f"Répartition des types MBTI sur " f"{ctx.guild.name}",
            colors=mbti_colors,
        )

        await ctx.reply(file=File(chart_image, "mbti_chart.png"))

    # Context commands --------------------------

    async def mood_from_message(
        self, interaction: Interaction, message: Message
    ) -> None:
        """
        Get the mood score for a specific message and send it as a progress bar.

        Args:
            interaction (discord.Interaction): The interaction representing the user's command.
            message (discord.Message): The message to analyze for mood score.
        """
        await interaction.response.defer(thinking=True)  # noqa

        guild_moods = self.get_guild_moods(message.guild)

        mood_score, mood_label = await self.bot.run_in_thread(
            guild_moods.get_message_mood, message.id, message.content
        )

        title = "Le score de {} pour ce [message]({}) est : ".format(
            mood_label, message.jump_url
        )

        progress_bar = f"{title}" + self.ascii_helper.get_progress_bar(mood_score)

        await interaction.followup.send(progress_bar)  # noqa

    async def sentiment_from_message(
        self, interaction: Interaction, message: Message
    ) -> None:
        """
        Get the positivity and the point of view score for a specific message and send them as a progress bar.

        Args:
            interaction (discord.Interaction): The interaction representing the user's command.
            message (discord.Message): The message to analyze for positivity score.
        """
        await interaction.response.defer(thinking=True)  # noqa

        guild_moods = self.get_guild_moods(message.guild)

        positivity_score = await self.bot.run_in_thread(
            guild_moods.get_message_positivity, message.id, message.content
        )

        pov_score = await self.bot.run_in_thread(
            guild_moods.get_message_pov, message.id, message.content
        )

        title_1 = "Le score de positivité pour ce [message]({}) est : ".format(
            message.jump_url
        )

        title_2 = "Le score de subjectivité pour ce [message]({}) est : ".format(
            message.jump_url
        )

        progress_bar = (
            f"{title_1}"
            + self.ascii_helper.get_progress_bar(positivity_score)
            + "\n"
            + f"{title_2}"
            + self.ascii_helper.get_progress_bar(pov_score)
        )

        await interaction.followup.send(progress_bar)  # noqa

    async def mbti_from_message(
        self, interaction: Interaction, message: Message
    ) -> None:
        """
        Get the dominant MBTI type for a message.

        Args:
            interaction (discord.Interaction): The interaction representing the user's command.
            message (discord.Message): The message to analyze for MBTI type.
        """
        await interaction.response.defer(thinking=True)  # noqa

        mbti_instance = self.get_guild_mbti(message.guild)

        mbti_result = await self.bot.run_in_thread(
            mbti_instance.get_message_mbti, message.content
        )

        dominant_type = max(mbti_result, key=mbti_result.get)

        mbti_type_link = f"https://www.16personalities.com/fr/la-personnalite-{dominant_type.lower()}"

        response_message = (
            f"Le type MBTI dominant pour le [message]({message.jump_url}) est : **{dominant_type}** "
            f":tada:\n"
        )
        response_message += (
            f":mag: Voici plus d'infos sur ce type : {mbti_type_link} :eyes:"
        )

        await interaction.followup.send(response_message)  # noqa


async def setup(bot: commands.Bot):
    await bot.add_cog(MoodsCog(bot))


async def teardown(bot: commands.Bot):
    await bot.remove_cog("MoodsCog")
    del sys.modules["util.moods"]
    del sys.modules["util.mbti"]
