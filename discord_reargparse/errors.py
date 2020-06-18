"""
MIT License

Copyright (c) 2020 NAVEEN S R

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
from discord.ext import commands

__all__ = ["NotMatchedWithPattern", "TooManyGroups", "NotEnoughGroups"]


class NotMatchedWithPattern(commands.UserInputError):
    """ Exception raised when argstr cannot be matched with pattern. """

    def __init__(self, pattern, argstr):
        super().__init__("Not matched with {0}: {1}".format(pattern, repr(argstr)))
        self.pattern = pattern
        self.argstr = argstr


class TooManyGroups(re.error):
    """ Exception raised when too many groups in pattern. """

    def __init__(self, nparams, ngroups):
        super().__init__("Too many groups for {0} parameters: {1} groups".format(nparams, ngroups))
        self.nparams = nparams
        self.ngroups = ngroups


class NotEnoughGroups(re.error):
    """ Exception raised when not enough groups in pattern. """

    def __init__(self, nparams, ngroups):
        super().__init__(
            "Not enough groups for {0} parameters: {1} groups".format(nparams, ngroups)
        )
        self.nparams = nparams
        self.ngroups = ngroups
