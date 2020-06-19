import discord
from discord.ext import commands
from discord_reargparse import *
import random
import shlex

description = "An example bot to showcase the discord_reargparse module."

bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

re_convert = RegExArgConverter(
    r"(\d+) (\d+)",
    left = Parameter(int),
    right = Parameter(int),
    )

@bot.command()
async def add(ctx, *, param:re_convert=re_convert.defaults):
    """Adds two numbers together."""
    await ctx.send(param["left"] + param["right"])

re_convert = RegExArgConverter(
    r"(\d+d\d+)",
    dice = Parameter(),
    )

@bot.command()
async def roll(ctx, *, param:re_convert=re_convert.defaults):
    """Rolls a dice in NdN format."""
    rolls, limit = map(int, param["dice"].split('d'))

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)

re_convert = RegExArgConverter(
    r"(\S+)",
    choices = Parameter(shlex.split),
    )

@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *, param:re_convert=re_convert.defaults):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(param["choices"]))

re_convert = RegExArgConverter(
    r"(\d+)(?:\ (\S+))?",
    times = Parameter(int),
    content = Parameter(default='repeating...'),
    )

@bot.command()
async def repeat(ctx, *, param:re_convert=re_convert.defaults):
    """Repeats a message multiple times."""
    for i in range(param["times"]):
        await ctx.send(param["content"])

re_convert = RegExArgConverter(
    r"(\S+)",
    member = Parameter(discord.Member),
    )

@bot.command()
async def joined(ctx, *, param:re_convert=re_convert.defaults):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(param["member"]))

@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

bot.run('token')
