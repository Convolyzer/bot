import discord
from discord.ext import commands, tasks
from core import Convolyzer, Store  # noqa
from util.jail import JailStore, JailConfig
import sys


class AdminCog(commands.Cog, name="Administration et Modération"):
    """
    Un bot pour les contrôler tous, un bot pour les gouverner tous...
    Voici le module qui contient du pouvoir en barre ! \
    Le pouvoir implique de grandes responsabilités, alors fait attention, OK ? :eyes:
    """

    def __init__(self, bot: Convolyzer) -> None:
        self.bot = bot
        self.jail_store = JailStore(Store("jail", bot.sql_con))
        # Timers
        self.flush_jail_store.start()
        self.unjail_members.start()

    async def cog_unload(self) -> None:
        self.flush_jail_store.stop()
        self.unjail_members.stop()
        self.jail_store.flush()

    # Utilities -------------------------------------------

    async def create_jail_rule(self, guild: discord.Guild) -> discord.AutoModRule:
        """Create a new automod rule for the jail."""
        # Define settings
        trigger = discord.AutoModTrigger(
            type=discord.AutoModRuleTriggerType.keyword_preset,
            presets=discord.AutoModPresets.all(),
        )
        actions = [discord.AutoModRuleAction()]
        event_type = discord.AutoModRuleEventType.message_send
        # Create the rule
        rule = await guild.create_automod_rule(
            name="Convolyzer Prison",
            trigger=trigger,
            actions=actions,
            event_type=event_type,
            enabled=True,
        )
        return rule

    async def create_jail_channel(
            self, guild: discord.Guild, role: discord.Role
    ) -> discord.TextChannel:
        """Create a new channel for the jail."""
        overwrites = {
            role: discord.PermissionOverwrite(read_messages=True),
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        channel = await guild.create_text_channel("Prison", overwrites=overwrites)
        return channel

    async def create_jail_role(self, guild: discord.Guild) -> discord.Role:
        """Create a new role for the jail."""
        # set the permisions
        permissions = discord.Permissions.text()
        permissions.read_messages = False
        permissions.read_message_history = False
        # create the role
        role = await guild.create_role(name="Prison", permissions=permissions)
        await role.edit(position=guild.me.top_role.position - 1)
        # overwrite in all channel!
        for channel in guild.channels:
            await channel.set_permissions(role, send_messages=False)
        return role

    async def notify_jail(self, channel: discord.TextChannel, member: discord.Member):
        embed = discord.Embed(
            title=":police_officer: Gardien de la prison",
            description=f"{member.display_name} vient d'arriver en prison :chains: !",
            color=discord.Color.red(),
        )
        await channel.send(embed=embed)

    async def notify_unjail(self, channel: discord.TextChannel, member=discord.Member):
        embed = discord.Embed(
            title=":police_officer: Gardien de la prison",
            description=f"{member.display_name} est libre :tada: !",
            color=discord.Color.green(),
        )
        await channel.send(embed=embed)

    def resolve_jailconf(self, guild: discord.Guild, jailconf: JailConfig):
        """Returns the discord objects for this jail."""
        rule_id = jailconf.get_rule()
        role = guild.get_role(jailconf.get_role())
        channel = guild.get_channel(jailconf.get_channel())
        return rule_id, role, channel

    # Timers ----------------------------------------------

    @tasks.loop(minutes=30)
    async def flush_jail_store(self):
        """Save the jail store on the disk."""
        self.jail_store.flush()

    @tasks.loop(minutes=1)
    async def unjail_members(self):
        """Unjail members after some time."""
        for guild_id, users in self.jail_store.free_prisoners().items():
            guild = self.bot.get_guild(guild_id)
            # get the jailconfig
            jailconf = self.jail_store.get(guild.id)
            if not jailconf:
                continue
            # get discord objects
            _, role, channel = self.resolve_jailconf(guild, jailconf)
            # check the jail
            if (not role) and (not channel):
                self.jail_store.delete_jail(guild_id)
                continue
            for user_id in users:
                member = guild.get_member(user_id)
                if not member:
                    continue
                if jailconf.has_prisoner(member.id):
                    continue
                await member.remove_roles(role)
                await self.notify_unjail(channel, member)

    # Events ----------------------------------------------

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction):
        member = execution.member
        if not member:
            return
        # get the jail config
        guild = execution.guild
        # get and check jailconfig
        jailconf = self.jail_store.get(guild.id)
        if not jailconf:
            return
        # get and check the discord objects
        rule_id, role, channel = self.resolve_jailconf(guild, jailconf)
        if (not role) and (not channel):
            self.jail_store.delete_jail(guild.id)
            return
        # check the rule
        if rule_id != execution.rule_id:
            return

        # Send the warning message
        await member.send(":rotating_light: Évite de parler grossièrement, s'il te plaît :rotating_light: !")

        jailconf.warn(member.id)

        if jailconf.get_warns_count(member.id) >= 3 and not jailconf.has_prisoner(member.id):
            print("Ok")
            # add the role to the member!
            await member.add_roles(role)
            jailconf.add_prisoner(member.id)
            await self.notify_jail(channel, member)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        # some shortcuts
        guild = message.guild
        channel = message.channel
        author = message.author
        content = message.content.lower()
        # get the jail config
        jailconf = self.jail_store.get(guild.id)
        if not jailconf:
            return
        # check the jail
        _, role, jail_channel = self.resolve_jailconf(guild, jailconf)
        if (not role) and (not jail_channel):
            self.jail_store.delete_jail(guild.id)
            return
        # check the channel
        if channel != jail_channel:
            return
        # check if the user is a prisoner
        if not jailconf.has_prisoner(author.id):
            return
        # check the content
        if content == "pardon":
            jailconf.pardon(author.id)
            await message.add_reaction("👍")

    # Commands --------------------------------------------

    @commands.command(brief="Création de la prison.")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def jailsetup(self, ctx: commands.Context):
        """
        La commande qui permet d'imposer le respect dans ton serveur. \
        Une fois mise en place, tu devrais sentir ses effets rapidement sur tes membres ;)
        """
        guild = ctx.guild
        # Fetch all automod rules from the guild
        automod_rules = await guild.fetch_automod_rules()
        # Check if the rule already exists
        existing_rule = None
        for r in automod_rules:
            if r.name == "Convolyzer Prison":
                existing_rule = r
                break

        if existing_rule:
            rule = existing_rule
        else:
            rule = await self.create_jail_rule(guild)
        role = await self.create_jail_role(guild)
        channel = await self.create_jail_channel(guild, role)

        # save that in the jail store
        self.jail_store.create_jail(guild.id, rule.id, role.id, channel.id)
        # the jail is ready!
        await ctx.reply("La prison est prête :tada: !")

    @commands.command(brief="Affiche les informations sur la prison.")
    async def jailshow(self, ctx: commands.Context):
        """
        Envie de jeter un œil aux paramètres de ta prison ? de vérifier si tout est bon ?
        Alors cette commande sert juste à ça ! Et oui, ça peut être utile parfois, non ?
        """
        guild = ctx.guild
        # get all config
        jailconf = self.jail_store.get(guild.id)
        if not jailconf:
            await ctx.reply("La prison n'existe pas :eyes: !")
            return
        # check the jail
        rule_id, role, channel = self.resolve_jailconf(guild, jailconf)
        if (not role) and (not channel):
            self.jail_store.delete_jail(guild.id)
            return

        if channel is None:
            await ctx.reply("La prison n'existe pas :eyes: !")
            return

        # create the embed
        embed = discord.Embed(
            title="Informations sur la prison",
        )
        embed.add_field(name="Règle Automod :", value=rule_id, inline=False)
        embed.add_field(name="Salon :", value=channel.name, inline=False)
        embed.add_field(name="Role :", value=role.name, inline=False)
        # send the embed
        await ctx.reply(embed=embed)

    @commands.command(brief="Emprisonne un membre *inoffensif*.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def jail(self, ctx: commands.Context, member: discord.Member):
        """
        Cette commande est l'arme ultime du modérateur ! \
        Envoie le membre spécifié directement en prison pour **5 minutes** ! \
        C'est simple, rapide et efficace, mais dangereusement addictif ! \
        Alors fait attention quand même >_<.
        """
        guild = ctx.guild
        jailconf = self.jail_store.get(guild.id)
        if not jailconf:
            await ctx.reply("La prison n'existe pas :eyes: !")
            return
        _, role, channel = self.resolve_jailconf(guild, jailconf)
        if not role:
            await ctx.reply("Il n'y a pas de prison ici :eyes: !")
            return
        if jailconf.has_prisoner(member.id):
            await ctx.reply(f"{member.display_name} est déjà en prison :chains: !")
            return

        jailconf.warn3(member.id)
        await member.add_roles(role)
        jailconf.add_prisoner(member.id)
        await ctx.send(f"{member.display_name} est en prison :chains: !")
        if channel:
            await self.notify_jail(channel, member)

    @commands.command(brief="Libère un membre de la prison.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unjail(self, ctx: commands.Context, member: discord.Member):
        """
        Si tu juges que le membre a assez purgé sa peine, tu peux le libérer avec cette commande. \
        Elle est moins addictive, mais tu vas peut-être te faire plus d'amis avec, non ?
        """
        guild = ctx.guild
        jailconf = self.jail_store.get(guild.id)
        if not jailconf:
            await ctx.reply("La prison n'existe pas :eyes: !")
            return
        _, role, channel = self.resolve_jailconf(guild, jailconf)
        if not role:
            await ctx.reply("Il n'y a pas de prison ici :eyes: !")
            return
        if not role in member.roles:
            await ctx.send(f"{member.display_name} n'est pas en prison :eyes: !")
            return
        await member.remove_roles(role)
        jailconf.free_prisoner(member.id)
        await ctx.reply(f"{member.display_name} n'est plus en prison :tada: !")
        if channel:
            await self.notify_unjail(channel, member)

    @commands.command(brief="Un brin de ménage dans le salon.")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, n: int):
        """
        Parfois, ça fait du bien un petit ménage pour faire le vide... \
        Et bien ici c'est important aussi ! \
        Lache toi et fait le vide des n derniers messages :broom:.
        """
        if n == 0:
            await ctx.send(
                "Indique le nombre de messages à supprimer s'il te plaît :pray:"
            )
        else:
            await ctx.channel.purge(limit=n + 1)  # +1 to include the command itself


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))


async def teardown(bot: commands.Bot):
    await bot.remove_cog("AdminCog")
    del sys.modules["util.jail"]
