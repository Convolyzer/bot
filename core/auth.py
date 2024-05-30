from discord.ext import commands
import discord

from core.store import Store


class AuthManager:
    def __init__(self, store: Store) -> None:
        self.__store = store
        self.__cache = dict()

    def is_allowed(self, user_id: int) -> bool:
        """
        Returns true if the user has agreed to the use of their data.
        """
        if user_id not in self.__cache:
            res = self.__store.get(user_id)
            self.__cache[user_id] = res if res is not None else True
        return self.__cache[user_id]

    def allow(self, user_id: int) -> None:
        """
        Defines that the user has agreed to the use of their data.
        """
        if self.is_allowed(user_id):
            return
        self.__store.set(user_id, (True,))
        self.__cache[user_id] = True

    def disallow(self, user_id: int) -> None:
        """
        Defines that the user has refused the use of their data
        """
        if not self.is_allowed(user_id):
            return
        self.__store.set(user_id, (False,))
        self.__cache[user_id] = False


class AuthConfirmView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__()
        self.user = user
        self.value = None

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.user

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.blurple)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        name = interaction.user.display_name
        await interaction.response.send_message(
            f"Merci de ta confiance {name} :tada:."
        )
        self.value = True
        self.stop()

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.danger)
    async def revoke(self, interaction: discord.Interaction, button: discord.ui.Button):
        name = interaction.user.display_name
        await interaction.response.send_message(
            f"Je comprends et je respecterai ton choix, {name} ... N'oublie pas de l'activer dès que tu changes ton "
            f"avis :pray: !"
        )
        self.value = False
        self.stop()


# Commands --------------------------------------

@commands.command(name="privacy", brief="Autorise ou non l'utilisation de tes données")
async def privacy_cmd(ctx: commands.Context):
    """
    Une simple commande pour te permettre de contrôler tes préférences en terme de vie privé. \
    Tes données, il faut les protéger des mauvaises personnes, mais moi je suis un gentil bot :)
    """
    auth_manager = ctx.bot.auth_manager
    view = AuthConfirmView(ctx.author)

    if not auth_manager.is_allowed(ctx.author.id):
        current = "Accepte s'il te plaît :grin:."
    else:
        current = "Ne me prive pas de tes messages s'il te plaît :sob: !"

    content = (
        f":wave: Salut {ctx.author.mention}! Je suis Convolyzer, un bot qui"
        " analyse tes messages et ceux des autres membres :eyes:. Tu m'autorise à "
        f"analyser tes messages ? ({current})."
    )

    await ctx.send(content, view=view)

    await view.wait()
    if view.value is None:
        return
    if view.value:
        auth_manager.allow(ctx.author.id)
    else:
        auth_manager.disallow(ctx.author.id)