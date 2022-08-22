import random
import subprocess
from typing import List, Tuple

import discord
from discord import Message
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import config
import helper
import quotes


class GameButler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Sets bot activity and posts bot name and id.
    @commands.Cog.listener()
    async def on_ready(self):
        await helper.log(f"Initialising {self.bot.user.name} #{self.bot.user.id}")
        await helper.log(random.choice(quotes.glados_startup))
        await helper.log('------')
        await self.bot.change_presence(activity=discord.Game(name=random.choice(quotes.activities)))

    # Chat Watch
    @commands.Cog.listener()
    async def on_message(self, message: Message):  
        if message.author == self.bot.user:
            return

        if type(message.channel) != discord.TextChannel:
            message_split = message.content.split(" ")
            if message_split[0] == "--report":
                if len(message_split) == 2 or len(message_split) == 1:
                    await message.reply("Hi there! I see you are trying to report an incident that occured relating to GameSoc. To make a report, please use '--report @user <explanation>' with an explanation of the incident that occured, making sure to say whether it was online or offline. Thanks! :heart:")
                    return
                    
                user = message_split[1]
                explanation = " ".join(message_split[2:])
                ticket_channel = self.bot.get_channel(config.TICKET_CHANNEL)
                await ticket_channel.send(f'A report was made against {user} with an explanation of {explanation}. <@&{config.COMMITTEE_ROLE}> <@&{config.MODERATOR_ROLE}>')
                await message.reply("Your report has been sent to moderators and committee, we hope to talk to you soon! :heart:")
            return  # doesn't reply to DMs or group chats that aren't incident repoorts

        await self.quotes(message)
        return

    async def quotes(self, message: Message) -> None:
        content, author, channel, guild = helper.read_message_properties(message)

        mappings: List[Tuple[str, str]] = [
            ("99", random.choice(quotes.brooklyn_99_quotes)),
            ("glados", f"```{random.choice(quotes.glados_quotes)}```"),
            ("lemons", f"```{random.choice(quotes.lemon_quotes)}```"),
            ("if life gives you lemons", quotes.lemonade),
            ("fortune", f"```{quotes.fortune()}```"),
            ("moo", f"```{quotes.moo()}```"),
            ("meeba", quotes.misha),
            ("misha", quotes.misha),
            ("f", f"{author.mention} sends their respects"),
            ("awooga", quotes.copypasta1),
            ("divide by zero", quotes.error_quote()),
            (f"<@!{self.bot.user.id}>", quotes.insult_quote())
        ]

        for (trigger, response) in mappings:
            if content.lower() == trigger:
                await message.reply(response)
                break

    @cog_ext.cog_slash(name="restart", description="Restart this bot", guild_ids=config.GUILD_IDS, options=[])
    @commands.has_role(config.BOT_ADMIN_ROLE)
    async def restart(self, ctx: SlashContext):
        self.bot.git_update = False
        self.bot.restart = True
        await ctx.send("Restarting...")
        await self.bot.close()

    @cog_ext.cog_slash(name="update", description="Update this bot", guild_ids=config.GUILD_IDS, options=[])
    @commands.has_role(config.BOT_ADMIN_ROLE)
    async def update(self, ctx: SlashContext):
        self.bot.git_update = True
        self.bot.restart = True
        await ctx.send("Updating...")
        await self.bot.close()

    @cog_ext.cog_slash(name="reload-cog", description="Reload a specific Cog", guild_ids=config.GUILD_IDS,
                       options=[helper.string_slash_command_option("cog", "Name of Cog to reload")])
    @commands.has_role(config.BOT_ADMIN_ROLE)
    async def reload_cog(self, ctx: SlashContext, cog: str):
        await helper.log(f"{ctx.author.display_name} reloaded {cog}")
        self.bot.reload_extension(cog)
        await ctx.send("Reloaded " + cog)

    @reload_cog.error
    async def reload_cog_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.errors.ExtensionNotLoaded):
            await ctx.send("Unknown Cog: " + str(error))
        else:
            raise error

    @cog_ext.cog_slash(name="sync-commands", description="Try to force slash command sync", guild_ids=config.GUILD_IDS,
                       options=[])
    @commands.has_role(config.BOT_ADMIN_ROLE)
    @commands.cooldown(1, 60.0, commands.BucketType.default)
    async def sync_commands(self, ctx: SlashContext):
        await helper.log(f"{ctx.author.display_name} triggered command resync")
        await ctx.slash.sync_all_commands()
        await ctx.send("Re-synced all commands")

    @sync_commands.error
    async def sync_commands_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(f"Failed to sync commands! {error}")

    @cog_ext.cog_slash(name="git-pull", description="Do a git pull", guild_ids=config.GUILD_IDS, options=[])
    @commands.has_role(config.BOT_ADMIN_ROLE)
    async def git_pull(self, ctx: SlashContext):
        await helper.log(f"{ctx.author.display_name} began a git pull")
        output = subprocess.Popen("git pull", shell=True, stdout=subprocess.PIPE).communicate()[0]
        await helper.log(str(output))
        await ctx.send("Git pull completed")



def setup(bot: commands.Bot):
    bot.add_cog(GameButler(bot))
