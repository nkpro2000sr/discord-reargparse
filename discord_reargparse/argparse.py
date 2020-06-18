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
import inspect
from discord.ext import commands
from .errors import *

__all__ = ["RegExArgConverter", "Parameter"]


class Parameter:
    """ To define a parameter """

    def __init__(self, converter=inspect.Parameter.empty, default=inspect.Parameter.empty):
        """ Initializes a Parameter.
        
        Args:
            converter:
                The converter to use. This follows the requirements of a
                :class:`discord.ext.commands.Converter`.
                a.k.a. annotation.
            default (object):
                The default value to use for DefaultParameter (Regex Optional Groups).
                If default value is :class:`inspect.Parameter.empty`,
                then parameter is considered as an OptionalParameter
                (the argument won't be included in the results).
        """

        self.converter = converter
        self.default = default


class Arguments(dict):
    """ Parsed arguments """

    def __init__(self, pattern, params, *args, **kwargs):
        """ Arguments parsed from argstr using pattern.
        
        Mapping of param => argument
        
        Args:
            pattern (re.Pattern):
                The Regex pattern to capture groups (args) from argstr.
            params (List(str)):
                The list of params.
        """
        self.pattern = pattern
        self.params = params
        super().__init__(*args, **kwargs)

    def __repr__(self):
        repr_params = []
        for param in self.params:
            if param in self:
                arg = self[param]
                repr_param = "[{0}={1}]".format(param, arg)
                repr_params.append(repr_param)
            else:
                repr_param = "<{0}>".format(param)
                repr_params.append(repr_param)
        return "Args(r'{0}' => {1})".format(self.pattern.pattern, " ".join(repr_params))

    # def __str__(self):
    # return str(self.copy())


class RegExArgConverter(commands.Converter):
    r""" Provides support for parsing arguments based on regex pattern in commands.
    
    By using this converter, users can parse arguments from user input 
    by capturing groups using a regex pattern
    For example::
    
        #For pattern '(\d+)?(\w+)?' => name, id
        
        !whois nkpro # name = 'nkpro'
        !whois 12345 # id   = 12345
    
    To use it, create an instance of this class and pass to it pattern and parameters.
    Then create a single keyword-only argument and annotate
    its type using the instance of this class.
    
    .. code-block: python3
    
        param_converter = RegExArgConverter(
            r"^(\S+[\ \S]*?)(?:\ -c(\d+))?(\ -n)?$",
            # OR re.compile(r"^(\S+[\ \S]*?)(?:\ -c(\d+))?(\ -n)?$"),
            
            string = Parameter(
                default="hello!",
            ),
            count = Parameter(
                int,
                default=2,
            ),
            new_line = Parameter(
                lambda x: bool(x),
            )
        )
        
        # ...
        
        @bot.command()
        async def repeat(ctx, *, params:param_converter=param_converter.defaults):
            string = params["string"]
            count = params["count"]
            sep = "\n" if params.get("new_line", False) else " "
            
            await ctx.send(sep.join([string]*count))
        
        @repeat.error
        async def repeat_error(ctx, error):
            if isinstance(error, NotMatchedWithPattern):
                await ctx.send(
                    "{0} not matched with pattern r'{1}'".format(
                        repr(error.argstr), error.pattern.pattern,
                    )
                )
    
    By using ``param_converter.defaults``, the ``params`` dict (Arguments)
    is initialized with the default values supplied.
    
    In case an error is encountered while matching the argstr, an
    :class:`NotMatchedWithPattern` exception is raised.
    Which is subclass of :class:`discord.ext.commands.UserInputError`.
    
    argstr : The input from beginning or middle up to the end.
             (also) The argument of the above mentioned single keyword-only parameter.
    """

    def __init__(self, pattern, **parameters):
        """ Initializes the RegEx based argument parser a.k.a converter.
        
        Args:
            pattern (Union[str, re.Pattern]):
                RegEx pattern to match and capture groups from.
            **parameters (Parameter):
                A mapping of parameter_name to :obj:`Parameter`.
        
        Raises:
            TooManyGroups: when more number of groups in pattern than parameters
            NotEnoughGroups: when not enough groups in pattern for parameters
        """

        if type(pattern) is str:
            pattern = re.compile(pattern)

        nparams = len(parameters.keys())
        ngroups = pattern.groups
        if ngroups > nparams:
            raise TooManyGroups(nparams, ngroups)
        elif ngroups < nparams:
            raise NotEnoughGroups(nparams, ngroups)

        self.pattern = pattern
        self.parameters = list()
        for param_name, parameter in parameters.items():
            self.parameters.append(
                inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_ONLY,
                    default=parameter.default,
                    annotation=parameter.converter,
                )
            )

    async def convert(self, ctx, argstr):
        converted = Arguments(self.pattern, [param.name for param in self.parameters])

        match = self.pattern.match(argstr)
        if match is None:
            raise NotMatchedWithPattern(self.pattern, argstr)

        arguments = match.groups()
        for parameter, argument in zip(self.parameters, arguments):

            if argument is None:  # For Regex Optional Groups
                if parameter.default is not inspect.Parameter.empty:
                    converted[parameter.name] = parameter.default
            else:
                converter = ctx.command._get_converter(parameter)
                converted[parameter.name] = await ctx.command.do_conversion(
                    ctx, converter, argument, parameter
                )

        return converted

    @property
    def defaults(self):
        """ Returns the arguments default values. """

        default_arguments = Arguments(self.pattern, [param.name for param in self.parameters])
        for parameter in self.parameters:
            if parameter.default is not inspect.Parameter.empty:
                default_arguments[parameter.name] = parameter.default
        return default_arguments
