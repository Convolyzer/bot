import io
import sys
import asyncio
from typing import Any, Generator
import os
from os import path
import discord
from math import floor
from discord import Message
from discord.ext import tasks, commands
from util.socialgraph import SocialGraph
from util.ascii import AsciiHelper


class CommunityCog(commands.Cog, name="Communauté"):
    """
    Les commandes de ce module vont te permettre d'en apprendre plus sur les \
    interactions entre les différents membres de ta communauté.
    L'objectif est de te permettre à toi et à tes amis d'analyser vos liens et \
    peut-être aussi de vous faire de nouveaux amis à l'aide d'algorithmes \
    avancés et d'une touche de magie :sparkles:. 
    """

    DATA_DIR = "data/graph"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.__guild_to_graph = dict()
        self.__load_all_graph()
        # timers
        self.update.start()

    def cog_unload(self):
        self.update.cancel()
        self.__save_all_graph()

    # ----------
    # Utility
    # ----------

    def __save_all_graph(self):
        for graph in self.__guild_to_graph.values():
            graph.save()

    def __load_all_graph(self):
        guild_ids = set()
        for file in os.listdir(self.DATA_DIR):
            guild_id = int(file.split(".")[0])
            guild_ids.add(guild_id)
        for guild_id in guild_ids:
            filepath = path.join(self.DATA_DIR, str(guild_id))
            socialgraph = SocialGraph(filepath, load=True)
            self.__guild_to_graph[guild_id] = socialgraph

    def get_graph(self, guild_id: int) -> SocialGraph:
        """
        Returns the social graph instance for the specified guild.
        """
        if not guild_id in self.__guild_to_graph:
            filepath = path.join(self.DATA_DIR, str(guild_id))
            self.__guild_to_graph[guild_id] = SocialGraph(filepath)
        return self.__guild_to_graph[guild_id]

    def __get_channel_cached_messages(
        self, channel_id: int
    ) -> Generator[Message, Any, None]:
        """
        Returns the list of cached message in this channel.
        """
        return (
            msg
            for msg in self.bot.cached_messages[::-1]
            if msg.channel.id == channel_id
        )

    # ----------
    # Timers
    # ----------

    @tasks.loop(minutes=1)
    async def update(self):
        """
        Run the update process of all socialgraph instances.
        """
        futures = []
        for socialgraph in self.__guild_to_graph.values():
            futures.append(self.bot.run_in_thread(socialgraph.update))
        await asyncio.gather(*futures)

    # ----------
    # Events
    # ----------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # check privacy setting
        if not self.bot.auth_manager.is_allowed(message.author.id):
            return

        socialgraph = self.get_graph(message.guild.id)

        # direct mention
        target_users = set()
        for member in message.mentions:
            if not member.bot:
                target_users.add(member.id)

        # reply target
        if message.reference:
            ref_msg = message.reference.resolved
            if isinstance(ref_msg, discord.Message):
                if not ref_msg.author.bot:
                    target_users.add(ref_msg.author.id)

        # (author_id, [target_users_id...], time)
        msg_data = (
            message.author.id,
            list(target_users),
            message.created_at.timestamp(),
        )

        # get other messages
        others_msgs = []
        for msg in self.__get_channel_cached_messages(message.channel.id):
            if msg.author.bot or msg.channel != message.channel:
                continue
            others_msgs.append(
                (
                    msg.author.id,
                    msg.created_at.timestamp(),
                )
            )
            # break when we have enought messages
            if len(others_msgs) == 10:
                break

        socialgraph.handle_message(msg_data, others_msgs)

    # ----------
    # Commands
    # ----------

    @commands.command(brief="Envoie l'image du graphe social.")
    async def socialgraph(self, ctx: commands.Context, user: discord.Member = None):
        """
        Envoie le graphe social de l'utilisateur ou celui de l'utilisateur mentionné. \
        La couleur du nœud représente l'importance de l'utilisateur dans le serveur (le rouge est le plus important). \
        La taille des arêtes représente l'importance de l'échange comparé aux autres échanges *affichés*. \
        Le curseur rouge permet de voir l'intérêt que les membres ont l'un pour l'autre. \
        Plus la zone entre vous et le curseur est grande, plus votre intérêt pour le membre cible est important.
        Bonne analyse !
        *PS : ne vous disputez pas trop >_<*
        """
        if not user:
            user = ctx.author

        socialgraph = self.get_graph(ctx.guild.id)

        pygv = socialgraph.to_pygraphviz(user.id, 10)

        # add username on each node
        for node in pygv.nodes_iter():
            user_id = int(str(node))
            node_user = ctx.guild.get_member(user_id) or self.bot.get_user(user_id)
            username = node_user.display_name if node_user else "?"
            node.attr["label"] = username

        # create an image and send it in the current channel
        pygv.layout("dot")
        img = io.BytesIO(pygv.draw(format="png"))
        file = discord.File(img, filename="socialgraph.png")
        await ctx.reply(
            f"Le graphe social de **{user.display_name}** :tada: :", file=file
        )

    @commands.command(brief="Affiche l'importance d'un membre.")
    async def importance(self, ctx: commands.Context, user: discord.Member = None):
        """
        Affiche ton importance ou celle du membre spécifié s'il est présent. \
        L'importance est relative au serveur entier. Essaye de dépasser tout le monde !
        """
        if not user:
            user = ctx.author

        socialgraph = self.get_graph(ctx.guild.id)

        result = socialgraph.get_importance(user.id)

        progress_bar = AsciiHelper.get_progress_bar(result)

        await ctx.reply(f"L'importance de {user.display_name} : {progress_bar}")

    @commands.command(brief="Affiche le rank social d'un membre.")
    async def socialrank(self, ctx: commands.Context, user: discord.Member = None):
        """
        Envie de savoir qui est le plus important plus facilement ? \
        Cette commande va afficher ton importance ou celle du membre spécifié. \
        Essaye de gravir les échelons complexes de la sociabilité !
        """
        if not user:
            user = ctx.author

        socialgraph = self.get_graph(ctx.guild.id)

        rank = socialgraph.get_rank(user.id)

        if rank is None:
            await ctx.reply(
                f"{user.display_name} n'a pas encore de rang dans ce server :sob:."
            )
        else:
            await ctx.reply(f"{user.display_name} est au rang {rank + 1} :tada: !")

    @commands.command(brief="Affiche le rang des membres les plus importants.")
    async def socialranks(self, ctx: commands.Context):
        """
        Affiche le rang des membres les plus importants. \
        Le rang social, ça se mérite ! Alors *active-toi un peu*, l'ami ! >_<
        """
        guild = ctx.guild
        socialgraph = self.get_graph(guild.id)

        top_ranks = socialgraph.get_top_ranks()

        lines = list()
        for i, user_id in enumerate(top_ranks):
            user = guild.get_member(user_id) or self.bot.get_user(user_id)
            name = user.display_name if user else "?"
            lines.append(f"{i + 1} - {name}")
        text = "\n".join(lines) if len(lines) > 0 else "Aucunes données :sob:."

        await ctx.reply(f"**__Les membres les plus importants :__**\n{text}")

    @commands.command(brief="Découvre *discrètement* le chemin vers ta proie.")
    async def socialpath(
        self,
        ctx: commands.Context,
        user_1: discord.Member,
        user_2: discord.Member = None,
    ):
        """
        Envoie la liste des gens que tu dois fréquenter pour parler à un membre.
        Tu peux:
        - Spécifier uniquement un membre pour avoir le chemin entre toi et lui.
        - Spécifier deux membres pour avoir le chemin qui les sépare.
        Amuse-toi et rencontre de nouvelles personnes ! *Fais attention quand même, hein ?*
        """
        guild = ctx.guild
        socialgraph = self.get_graph(guild.id)

        # define source and destination
        if not user_2:
            user_src = ctx.author
            user_dst = user_1
        else:
            user_src = user_1
            user_dst = user_2

        # get the path
        path = await self.bot.run_in_thread(
            socialgraph.get_social_path, user_src.id, user_dst.id
        )

        if len(path) == 0:
            await ctx.reply(
                f"Il n'existe pas de chemin entre **{user_src.display_name}** et **{user_dst.display_name}** :sob:."
            )
        else:
            lines = list()
            lines.append(
                f"**__Le chemin social entre {user_src.display_name} et {user_dst.display_name} :__**"
            )

            for i, user_id in enumerate(path):
                user = guild.get_member(user_id) or self.bot.get_user(user_id)

                if i == 0:
                    symbol = ":checkered_flag:"
                elif i == len(path) - 1:
                    symbol = ":dart:"
                else:
                    symbol = ":arrow_down:"
                
                name = user.display_name if user else "?"

                lines.append(f"{symbol} | {name}")

            text = "\n".join(lines)

            await ctx.reply(text)

    @commands.command(brief="Liste les interactions d'un membre.")
    async def interactions(self, ctx: commands.Context, user: discord.Member = None):
        """
        Affiche les gens à qui tu as parlé ou, si tu mentionnes un membre, la liste des gens auxquels il a parlé.
        Je n'affiche pas tous les membres ; s'il y en a trop, je garde les plus importants <3.
        """
        if not user:
            user = ctx.author

        guild = ctx.guild

        socialgraph = self.get_graph(ctx.guild.id)

        lines = list()
        for it_user_id in socialgraph.get_interactions(user.id, 10):
            it_user = guild.get_member(it_user_id) or self.bot.get_user(it_user_id)
            it_name = it_user.display_name if it_user else "?"
            lines.append(f"- {it_name}")

        if len(lines) == 0:
            lines.append(
                f"Il semble que **{user.display_name}** n'a aucune interaction avec des êtres humains :eyes:."
            )
        else:
            lines.insert(0, f"**__Interaction de {user.display_name} :__**")

        text = "\n".join(lines)

        await ctx.reply(text)

    @commands.command(brief="Affiche l'intérêt d'un membre pour un autre.")
    async def interest(
        self,
        ctx: commands.Context,
        user_1: discord.Member,
        user_2: discord.Member = None,
    ):
        """
        Pour afficher l'intérêt relatif d'un membre pour un autre, tu peux :
        - Spécifier un membre pour avoir l'intérêt que tu lui portes.
        - Spécifier deux membres pour afficher l'intérêt que le premier porte à l'autre.
        Cette commande est livrée telle quelle, je ne peux en aucun cas être responsable de déprime ou de conflit...
        """
        # define users
        if user_2:
            user_src = user_1
            user_dst = user_2
        else:
            user_src = ctx.author
            user_dst = user_1
        # get the graph
        socialgraph = self.get_graph(ctx.guild.id)
        # get the score from user_src to user_dst
        score = socialgraph.get_interest(user_src.id, user_dst.id)
        print(score)
        bar = AsciiHelper.get_progress_bar(score)
        await ctx.reply(
            "Intérêt de {} pour {} : {}".format(
                user_src.display_name, user_dst.display_name, bar
            )
        )

    @commands.command(brief="Trouve les membres qui matchent bien ensemble.")
    async def match(self, ctx: commands.Context, member: discord.Member = None):
        """
        Oh Discord ! Discord ! Tant de messages, tant de gens ! \
        Et si je te disais que je connais peut-être quelqu'un qui va changer ta vie ? \
        Quelqu'un qui saura te comprendre, parler avec toi sans complexe, s'amuser, te compléter… \
        Peut-être ton âme sœur se cache ici ? dans les tréfonds du serveur ? \
        Alors voici l'arme ultime ! Ta chance de changer ta vie ! Tu peux l'utiliser pour toi ou pour un membre !
        Amusez-vous, faites des rencontres ! Telle est ma mission >_<.
        """
        if member:
            fail_text = f"Aucun membre compatible avec {member.display_name}... :sob:"
            header_text = (
                f"Voici les membres compatibles avec {member.display_name} ! "
                "*J'espère que tu es satisfait de ce résultat...*"
            )
        else:
            member = ctx.author
            fail_text = "Aucun membre compatible avec toi... :sob:"
            header_text = (
                "Voici les membres compatibles avec toi ! "
                "J'espère que tu trouveras *quelqu'un* qui te correspond le plus :heart: !"
            )

        moods_cog = self.bot.get_cog_by_class_name("MoodsCog")
        if not moods_cog:
            await ctx.reply(
                "Désolé mais ette commande est indisponible pour le moment :sweat_smile:"
            )
            return

        compatible_members = moods_cog.get_compatible_members(ctx.guild, member)[:10]
        if not compatible_members:
            await ctx.reply(fail_text)
            return

        member_list = "\n".join(
            [f"- {member.display_name} ({floor(score*100)}%)" for member, score in compatible_members]
        )
        await ctx.reply(header_text + "\n" + member_list)


async def setup(bot: commands.Bot):
    await bot.add_cog(CommunityCog(bot))


async def teardown(bot: commands.Bot):
    await bot.remove_cog("CommunityCog")
    del sys.modules["util.socialgraph"]
    if "util.ascii" in sys.modules:
        del sys.modules["util.ascii"]
