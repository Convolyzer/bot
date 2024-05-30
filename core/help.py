import discord
from discord.ext import commands
from typing import Mapping, Optional, List

# UI --------------------------------------------


class Dropdown(discord.ui.Select):
    def __init__(self, cogs: List[commands.Cog], embed_cog_factory):
        self.cogs = cogs
        self.embed_cog_factory = embed_cog_factory

        options = []
        for i, cog in enumerate(self.cogs):
            option = discord.SelectOption(label=cog.qualified_name, value=i)
            options.append(option)

        super().__init__(
            placeholder="Sur quel groupe tu souhaites de l'aide?",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        cog = self.cogs[int(self.values[0])]
        embed = self.embed_cog_factory(cog)
        await interaction.response.edit_message(embed=embed)


class DropdownView(discord.ui.View):
    def __init__(self, user: discord.User, cogs: commands.Cog, embed_cog_factory):
        super().__init__()
        self.user = user
        # Adds the dropdown to our view object.
        self.add_item(Dropdown(cogs, embed_cog_factory))

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.user


# Help ------------------------------------------


class ConvolyzerHelp(commands.HelpCommand):
    def __init__(self) -> None:
        brief_text = "Affiche le menu d'aide."
        help_text = (
            "Tu ne peux pas t'amuser avec moi si tu ne me connais pas, non ? "
            "Avec cette commande, tu vas pouvoir explorer toutes mes fonctionnalités et t'amuser ! "
        )
        super().__init__(command_attrs={"brief": brief_text, "help": help_text})

    # Utilities ---------------------------------

    def get_base_embed(self) -> discord.Embed:
        author = self.context.author
        bot = self.context.bot
        bot_user = self.context.me
        color = discord.Color.from_str(bot.config.get_color())

        embed = discord.Embed(color=color)
        embed.set_footer(
            text=f"Demandé par {author.display_name}", icon_url=author.display_avatar
        )
        embed.set_thumbnail(url=bot_user.display_avatar.with_size(512))

        return embed

    def get_embed_main(self):
        # some shortcuts
        bot = self.context.bot
        prefix = self.context.clean_prefix
        command_name = self.context.command.name

        embed = self.get_base_embed()
        embed.title = "Menu d'aide"
        embed.description = (
            f"Salut ! Je suis {bot.user.display_name}, un bot super utile prêt à t'aider ! "
            "Je vais analyser tes conversations et tes amis avec un peu de magie ! "
            "*Tu n'en sauras pas plus ! Ce sont mes petits secrets...* "
            "J'espère pouvoir améliorer tes relations sociales et mieux comprendre le monde qui t'entoure ;)"
            "\n"
            f"Pour que je puisse t'aider, assure-toi bien d'avoir autorisé l'utilisation de tes messages avec la commande `{prefix}privacy`."
            "\n"
            f"Tu peux obtenir des infos sur toutes les commandes en utilisant `{prefix}help <commande>`, alors amuse-toi bien :tada:"
        )

        for cog in bot.cogs.values():
            embed.add_field(
                name=cog.qualified_name, value=cog.description, inline=False
            )

        return embed

    def get_embed_cog(self, cog: commands.Cog) -> discord.Embed:
        prefix = self.context.prefix
        embed = self.get_base_embed()
        cmds = "\n".join(
            [f"- `{prefix}{cmd.name}`: {cmd.brief}" for cmd in cog.get_commands()]
        )
        embed.title = cog.qualified_name
        embed.description = f"{cog.description}\n\n{cmds}"
        return embed

    def get_embed_command(self, cmd: commands.Command) -> discord.Embed:
        embed = self.get_base_embed()
        embed.title = f"Commande {cmd.name}"
        embed.description = cmd.help if cmd.help else "Aucune description :eyes:"
        embed.add_field(name="Utilisation :", value=self.get_command_signature(cmd))
        return embed

    async def send_embed_with_view(self, embed: discord.Embed):
        author = self.context.author
        view = DropdownView(
            author, list(self.context.bot.cogs.values()), self.get_embed_cog
        )
        await self.get_destination().send(embed=embed, view=view)

    # Overwrites --------------------------------

    def command_not_found(self, name: str) -> str:
        return f"La commande {name} n'existe pas :sob:."

    async def send_bot_help(
        self, _: Mapping[Optional[commands.Cog], List[commands.Command]]
    ):
        embed = self.get_embed_main()
        await self.send_embed_with_view(embed)

    async def send_cog_help(self, cog: commands.Cog):
        embed = self.get_embed_cog(cog)
        await self.send_embed_with_view(embed)

    async def send_command_help(self, cmd: commands.Command):
        embed = self.get_embed_command(cmd)
        await self.get_destination().send(embed=embed)
