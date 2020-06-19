from discord.ext import commands
from discord_reargparse import *

import re
import shlex

def _until_dh(splited):
    """ Slice until double hyphen """
    i = 0
    for i, s in enumerate(splited):
        if s == "--":
            return splited[:i], i + 1
        elif s.startswith("--"):
            return splited[:i], i
    return splited[:], i + 1

def shlex_argparse(argstr):
    """ Get positional arguments and optional arguments from argstr.
    
    Example::
    
       parse p1 p2 'p3 three' --o1=one '--o2=two' --o3='3 three' p'4 four' --o4 four Four
       
       as args = ['p1', 'p2', 'p3 three', 'p4 four']
       and kwargs = {'o1':'one', 'o2':'two', 'o3':'3 three', 'o4':['four', 'Four']}
    """

    args = shlex.split(argstr)
    differentiate = re.compile(r"^(?:(?:--(\w+)=([\s\S]*))|(?:--(\w+))|(\S[\s\S]*))$")

    positional_args = []
    optional_args = {}
    i = 0
    while i < len(args):
        match = differentiate.match(args[i])
        if match is None:
            raise re.error("Not matched", pattern=differentiate)
        key, value, var_key, pos = match.groups()
        if pos:
            if pos != "--":
                positional_args.append(pos)
        elif key:
            optional_args[key] = value
        elif var_key:
            optional_args[var_key], j = _until_dh(args[i + 1 :])
            i += j
        i += 1

    return positional_args, optional_args


description = """ To use not a RegEx pattern as pattern for RegExArgConverter """

bot = commands.Bot(command_prefix="?", description=description)

# class always_equal:
#     """ To avoid TooManyGroups and NotEnoughGroups exception """
#     def __lt__(self):
#         return False
#     def __gt__(self):
#         return False


class shlex_argparse_pattern:
    def __init__(self, groups=None):
        self.pattern = "Just shlex_argparsing"
        self._ngroups = 2
        self._groups = groups

    def match(self, string):
        groups = shlex_argparse(string)
        groups = tuple(groups)
        return shlex_argparse_pattern(groups)

    @property
    def groups(self):
        if self._groups is None:
            return self._ngroups
        else:
            def call():
                return self._groups
            return call


converter = RegExArgConverter(
    shlex_argparse_pattern(),
    args=Parameter(),
    kwargs=Parameter(),
)

@bot.command()
async def parse(ctx, *, param: converter = converter.defaults):
    """ parse positional and optional arguments from commands """
    await ctx.send(param["args"])
    await ctx.send(param["kwargs"])


bot.run("token")
