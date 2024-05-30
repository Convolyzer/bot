from discord.ext import commands
import traceback


class StaffCog(commands.Cog, name="Outils développeurs"):
    """
    La catégorie pour les maitres de l'univers ! Pas touche si tu n'en fais pas partie ! \
    *Sinon, je vais me fâcher très fort... ;)*
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        if self.bot.config.is_in_staff_team(ctx.author.id):
            return True
        else:
            raise commands.NotOwner()

    @commands.command(brief="Charge une extension.")
    async def load(self, ctx: commands.Context, ext_name):
        """
        Charge l'extension spécifiée comme si de rien n'était...
        """
        try:
            await self.bot.load_extension(f"ext.{ext_name}")
            await ctx.reply(f"Le module {ext_name} est chargé :tada: !")
        except:
            traceback.print_exc()
            await ctx.reply(f"Impossible de charger l'extension `{ext_name}` :sob: !")

    @commands.command(brief="Décharge une extension.")
    async def unload(self, ctx: commands.Context, ext_name):
        """
        Décharge l'extension, ça fait du bien de s'alléger l'esprit de ce poids !
        """
        try:
            await self.bot.unload_extension(f"ext.{ext_name}")
            await ctx.reply(f"Le module `{ext_name}` est déchargé !")
        except:
            traceback.print_exc()
            await ctx.reply(f"Impossible de décharger l'extension `{ext_name}` :sob: !")

    @commands.command(brief="Recharge les extensions.")
    async def reload(self, ctx: commands.Context, ext_name=None):
        """
        Recharge toutes les extensions avec *beaucoup* de style.
        """
        if ext_name is None:
            extensions = list(self.bot.extensions.keys())
        else:
            extensions = ["ext." + ext_name]
        try:
            nb_ext = len(extensions)
            for extension in extensions:
                await self.bot.reload_extension(extension)
            await ctx.reply(f"`{nb_ext}` extension(s) rechargée(s) :tada: !")
        except Exception:
            traceback.print_exc()
            await ctx.reply("Impossible de recharger les extensions :sob: !")

    @commands.command(brief="Bye !")
    async def bye(self, ctx: commands.Context):
        """
        Tu me boudes ? Tu ne veux plus me voir ? :sob:
        """
        await ctx.reply("Au revoir :wave: ! Prend soins de toi :kissing_heart: !")
        await self.bot.close()
