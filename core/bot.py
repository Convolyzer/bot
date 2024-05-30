import discord
from discord.ext import commands, tasks
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from transformers import pipeline
from typing import Any
from random import randint, choice

from core.config import Config
from core.translate import Translator
from core.staff import StaffCog
from core.store import Store
from core.auth import AuthManager, privacy_cmd
from core.help import ConvolyzerHelp


class Convolyzer(commands.Bot):
    def __init__(self, prefix, intents, config: Config) -> None:
        super().__init__(prefix, intents=intents, help_command=ConvolyzerHelp())
        # threads pool
        self.thread_pool = ThreadPoolExecutor()
        # the config manager
        self.config = config
        # db and store
        self.sql_con = sqlite3.connect("data/db.sqlite")
        self.privacy_store = Store("privacy", self.sql_con)
        # auth manager
        self.auth_manager = AuthManager(self.privacy_store)
        # the translator
        self.translator = Translator()
        # the pipelines
        self.pipeline_summary = pipeline(
            "summarization", model="moussaKam/mbarthez-dialogue-summarization"
        )
        self.pipeline_topics = pipeline(
            "text-classification", model="lincoln/flaubert-mlsum-topic-classification"
        )
        self.pipeline_mood = pipeline(
            "text-classification",
            model="botdevringring/fr-naxai-ai-emotion-classification-081808122023",
        )
        self.pipeline_sentiment = pipeline(
            "text-classification",
            model="citizenlab/twitter-xlm-roberta-base-sentiment-finetunned",
        )
        self.pipeline_mbti = pipeline(
            "text-classification", model="JanSt/albert-base-v2_mbti-classification"
        )
        # add globals check
        self.add_check(self.__globally_block_dms)

    async def run_in_thread(self, func, *args) -> Any:
        """Run the function in a thread and return the result"""
        future = self.loop.run_in_executor(self.thread_pool, func, *args)
        await future
        return future.result()
    
    def get_cog_by_class_name(self, name: str):
        """
        Returns the cog with this class name.
        Like get_cog but only work with the class name.
        """
        res = None
        for cog in self.cogs.values():
            if cog.__class__.__name__ == name:
                res = cog
                break
        return res

    @tasks.loop(seconds=30)
    async def update_status(self):
        if len(self.users) == 0:
            return
        user1 = choice(self.users)
        if randint(0, 1) == 0:
            # one target user
            texts = (
                "{} mange comme un champion !",
                "Je t'aime plus que le Nutella aime les crêpes, {}❤️",
                "Tu brilles comme un phare, {}!",
                "J'ai trouvé le bug {}.exe, je le fais danser !",
                "{} a avalé un citron...",
                "T'es une vraie rock star, {}! \o/",
                "{} a l'air d'un chaton trempé, pauvre chou...",
                "{}, t'es le/la meilleur(e)! Chut, c'est un secret !",
                "{} est digne de confiance, enfin j'espère...",
                "Les données de {} sont à vendre ! Qui veut des infos ?",
                "T'es un vrai génie, {}!",
                "Cher/Chère {}, passe une journée cool !",
                "{}, t'es une source d'inspiration, même pour les fourmis !",
                "Merci {}, je vais te kidnapper !",
                "{}, ton sourire brille comme un phare !",
                "Quel beau projet, {} ! Je suis impressionné(e) comme un poisson !",
                "{}, t'es tellement généreux/généreuse que ça devient suspect...",
                "Bravo {}, je suis fier/fière de toi comme un paon !",
                "{}, t'es exceptionnel(le), ne change pas... enfin si, un peu !",
                "{}, t'es une âme pure, comme un ange en carton.",
                "Merci {}, tu me soutiens même avec mes blagues nulles !",
                "{}, ton dynamisme est contagieux comme un rhume !",
                "Cher/Chère {}, t'es important(e) comme le sel dans les frites !",
                "{}, t'as un cœur en or, brille comme une boule à facettes !",
                "Félicitations {}, tu le mérites comme un chat mérite ses croquettes !",
                "{}, t'es unique comme un canard qui fait du vélo !",
                "Cher/Chère {}, je suis fier/fière de toi comme un parent fier !",
                "{}, ton optimisme est une inspiration, comme un rayon de soleil !",
                "Merci {}, tu me remontes le moral comme un ascenseur en panne !",
                "{}, t'es attentionné(e) comme une maman poule !",
                "Cher/Chère {}, j'ai confiance en toi comme un enfant en son doudou !",
                "{}, ton énergie est impressionnante, comme un lapin sous caféine !",
                "Félicitations {}, t'as tout donné comme un hamster dans une roue !",
                "{}, t'es généreux/généreuse comme un politicien qui promet !",
                "Cher/Chère {}, je suis fier/fière de t'avoir comme un chien est fier d'avoir son os !",
            )
            text = choice(texts).format(user1.display_name)
        else:
            # two target users
            user2 = choice(self.users)
            texts = (
                "{} et {} complotent comme des vilains !",
                "{} veut épouser {} comme un prince/une princesse charmant(e) <3",
                "{} peut faire un café à {} ? Avec de la mousse en forme de cœur !",
                "{} et {} sont mes petits chéris, trop mignons !",
                "{} a renversé son verre sur {}, quel(le) boulet !",
                "{} aime {} en cachette, comme un(e) ado !",
                "{} a offert un cadeau à {}, trop gentil(le) !",
                "{} et {} complotent comme des espions !",
                "{} a surpris {} en train de... se gratter le nez !",
                "{} a fait rire {}, quel(le) comédien(ne) !",
                "{} a aidé {} comme une maman/un papa poule !",
                "{} a fait un compliment à {}, trop mignon(ne) !",
                "{} a partagé son déjeuner avec {}, quel(le) partage !",
                "{} a fait une blague à {}, quel(le) humoriste !",
                "{} a consolé {} qui était triste, trop chou/choupette !",
                "{} a fait une surprise à {}, quel(le) filou/filou(te) !",
                "{} a prêté son stylo à {}, quel(le) gentleman/lady !",
                "{} a écouté {} avec attention, quel(le) ange !",
                "{} a fait un câlin à {}, trop mignon(ne) !",
                "{} a partagé son secret avec {}, quel(le) confident(e) !",
                "{} a fait rougir {}, quel(le) charmeur/charmeuse !",
                "{} a aidé {} à traverser, quel(le) héros/héroïne !",
                "{} a fait un high-five à {}, trop cool !",
                "{} a fait un jeu avec {}, quel(le) rigolo/rigolote !",
                "{} a fait un bisou à {}, quel(le) coquin(e) !",
                "{} a fait un cadeau à {}, quel(le) généreux/généreuse !",
                "{} a fait une farce à {}, quel(le) farceur/farceu(se) !",
                "{} a fait un sourire à {}, quel(le) rayon de soleil !",
                "{} a fait un clin d'oeil à {}, quel(le) charmeur/charmeuse !",
            )
            text = choice(texts).format(user1.display_name, user2.display_name)
        text = f"{self.config.get_prefix()}help | {text}"
        activity = discord.CustomActivity(text)
        await self.change_presence(activity=activity)

    async def setup_hook(self) -> None:
        # Load the privacy command
        self.add_command(privacy_cmd)
        # Load Cog in core
        await self.add_cog(StaffCog(self))
        # Load extensions
        extensions = ("admin", "moods", "community", "summary", "discover")
        for extension in extensions:
            await self.load_extension(f"ext.{extension}")
        # Sync app commands with discord
        if self.config.is_debug():
            test_guild = discord.Object(id=self.config.get_test_guild())
            self.tree.copy_global_to(guild=test_guild)
            await self.tree.sync(guild=test_guild)
        else:
            await self.tree.sync()
        # start the status update loop
        self.update_status.start()

    async def close(self) -> None:
        for extension in list(self.extensions.keys()):
            await self.unload_extension(extension)
        self.update_status.cancel()
        self.thread_pool.shutdown(cancel_futures=True)
        await super().close()

    async def __globally_block_dms(self, ctx):
        """Raise an exception if the message in not in a guild."""
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        else:
            return True

    async def on_command_error(
        self, ctx: commands.Context, err: commands.CommandError
    ) -> None:
        if isinstance(err, commands.CommandError):
            if isinstance(err, commands.UserInputError):
                await ctx.reply(
                    "Tu as fait une erreur dans la commande :sob:, jette un oeil à la commande d'aide "
                    "s'il te plaît :pray: !"
                )
                # stop here
                return
            elif isinstance(err, commands.CheckFailure):
                if isinstance(err, commands.NoPrivateMessage):
                    await ctx.reply(
                        "Tu ne peux pas utiliser cette commande ici :grin: !"
                    )
                elif isinstance(err, commands.NotOwner):
                    await ctx.reply(
                        "**Pas touche !!!** Cette commande est réservée au staff du bot :sunglasses: ! "
                        "*Merci :grin:* !"
                    )
                elif isinstance(err, commands.MissingPermissions):
                    await ctx.reply(
                        "Tu n'as pas les permissions nécessaires pour utiliser cette commande "
                        ":see_no_evil: !"
                    )
                elif isinstance(err, commands.BotMissingPermissions):
                    await ctx.reply(
                        "Je n'ai pas les permissions nécessaires pour exécuter cette commande :sob: !"
                    )
                else:
                    await ctx.reply(
                        "Tu ne peux pas utiliser cette commande pour *une bonne raison* :wink: !"
                    )
                # ignore other checks
                return
            elif isinstance(err, commands.CommandInvokeError):
                await ctx.send(
                    "Oups ... Une erreur interne s'est produite :ambulance: !"
                )
                await super().on_command_error(ctx, err)
        else:
            await super().on_command_error(ctx, err)
