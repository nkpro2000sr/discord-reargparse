import pytest
import discord_reargparse as da
from discord.ext import commands
from discord.ext import test as dpytest


@pytest.fixture
def bot(scope="module"):
    bot = commands.Bot(command_prefix="dummy")
    dpytest.configure(bot)
    return bot


@pytest.fixture
def command(bot):
    @bot.command()
    async def dummy(ctx):
        pass

    return dummy


@pytest.fixture
async def ctx(bot, command):
    message = await dpytest.message("dummy")
    ctx = commands.Context(bot=bot, message=message, prefix="dummy")
    ctx.command = command
    return ctx


@pytest.mark.asyncio
async def test_reargparse(ctx):
    converter = da.RegExArgConverter(
        r"^(\S+[\ \S]*?)(?:\ -c(\d+))?(\ -n)?$",
        string=da.Parameter(default="hello!",),  # Regex non-Optional Group (Required Parameter)
        count=da.Parameter(int, default=2,),  # Regex Optional Group (Default Parameter)
        new_line=da.Parameter(lambda x: bool(x),),  # Regex Optional Group (Optional Parameter)
    )

    with pytest.raises(da.NotMatchedWithPattern):
        await converter.convert(ctx, "")

    args = converter.defaults
    assert args["string"] == "hello!"
    assert args["count"] == 2
    assert "new_line" not in args.keys()

    with pytest.raises(da.NotMatchedWithPattern):
        await converter.convert(ctx, "Hello\nWorld")

    args = await converter.convert(ctx, "Hi")
    assert args["string"] == "Hi"
    assert args["count"] == 2
    assert "new_line" not in args.keys()

    args = await converter.convert(ctx, "Welcome :) -n")
    assert args["string"] == "Welcome :)"
    assert args["count"] == 2
    assert args["new_line"] == True

    args = await converter.convert(ctx, "#Enjoy -c1")
    assert args["string"] == "#Enjoy"
    assert args["count"] == 1
    assert "new_line" not in args.keys()
