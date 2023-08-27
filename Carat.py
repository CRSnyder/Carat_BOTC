import contextlib
import os
import traceback

import nextcord
import requests
from dotenv import load_dotenv
from nextcord.ext import commands
from nextcord.ext.commands import DefaultHelpCommand, CommandError

import utility
from Cogs.Archive import Archive
from Cogs.Game import Game
from Cogs.Grimoire import Grimoire
from Cogs.Other import Other
from Cogs.Reminders import Reminders
from Cogs.Signup import Signup
from Cogs.TextQueue import TextQueue
from Cogs.Townsquare import Townsquare
from Cogs.Users import Users
from utility import Helper

load_dotenv()
token = os.environ['TOKEN']

intents = nextcord.Intents.all()
allowedMentions = nextcord.AllowedMentions.all()
allowedMentions.everyone = False
help_command = DefaultHelpCommand(verify_checks=False, dm_help=None, dm_help_threshold=600)

bot = commands.Bot(command_prefix=">",
                   case_insensitive=True,
                   intents=intents,
                   allowed_mentions=allowedMentions,
                   activity=nextcord.Game(">HelpMe or >help"),
                   help_command=help_command)


# load cogs and print ready message
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('Loading cogs')
    helper = Helper(bot)
    bot.add_cog(Archive(bot, helper))
    bot.add_cog(Game(bot, helper))
    bot.add_cog(Grimoire(bot, helper))
    bot.add_cog(Other(bot, helper))
    bot.add_cog(Reminders(bot, helper))
    bot.add_cog(TextQueue(bot, helper))
    bot.add_cog(Signup(bot, helper))
    bot.add_cog(Users(bot, helper))
    votes_cog = Townsquare(bot, helper)
    await votes_cog.load_emoji()
    bot.add_cog(votes_cog)
    print('Ready')
    print('------')


@bot.event
async def on_command_error(ctx: commands.Context, error: CommandError):
    if isinstance(error, commands.CommandNotFound):
        # filter out emoji like >.> by checking if first character after > is a letter
        if ctx.message.content[1].isalnum() and not ctx.message.content[1].isdigit():
            await utility.dm_user(ctx.author, "Command not found. Use >help for a list of commands, "
                                              "or >HelpMe for a list of commands with explanations.")
    elif isinstance(error, commands.UserInputError):
        await utility.dm_user(ctx.author, f"There was an issue with your input. Usage: "
                                          f"`>{ctx.command.name} {ctx.command.signature}`.")
    else:
        print("An error occurred: " + str(error))
        traceback.print_exception(type(error), error, error.__traceback__)


@bot.command()
async def ReloadCogs(ctx: commands.Context):
    if ctx.author.id == 224643391873482753:
        await utility.start_processing(ctx)
        #TODO: unload extensions
        response = requests.get("https://api.github.com/repos/JackKBroome/Carat_BOTC/contents/Cogs",
                                      headers={"Accept": "application/vnd.github+json",
                                               "X-GitHub-Api-Version": "2022-11-28"})
        if response.status_code != 200:
            await utility.deny_command(ctx)
            await utility.dm_user(ctx.author, "Could not connect to GitHub")
            return
        for file in response.json():
            if file["name"].endswith(".py"):
                response = requests.get(file["download_url"])
                if response.status_code != 200:
                    await utility.deny_command(ctx)
                    await utility.dm_user(ctx.author, "Could not connect to GitHub")
                    return
                with open(os.path.join("Cogs", file["name"]), "w", encoding="utf-8") as f:
                    f.write(response.text)
                #TODO: load extensions
        await utility.finish_processing(ctx)
    else:
        await utility.deny_command(ctx)


bot.run(token)
