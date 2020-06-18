discord_reargparse
==================

Provides support for RegEx based argument parsing in commands for the
[discord.py](https://github.com/Rapptz/discord.py/) library.

```python
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
```

On your discord server, the commands can be invoked like this:

```
!repeat

> hello! hello!

!repeat Hi -c3 -n

> Hi
> Hi
> Hi

!repeat hello
world

    → will raise a NotMatchedWithPattern exception
```


Installation
------------

Installation is available via pip:

```
pip install discord_reargparse
```


Documentation
-------------

Initialize an `RegExArgConverter` as in the example above, annotate a
keyword-only function argument in your command with the instance and,
optionally, set its default value by using the `.defaults` attribute.
Setting a default value can be omitted for non-optional regex groups.

It will raise a `NotMatchedWithPattern` exception if not matched
with given regex pattern.

Inside the command, you can access the arguments as a dict.


command's usage
---------------

The usage string of repeat command is displayed like.
```
!help repeat

> repeat [params=Args(r'^(\S+[\ \S]*?)(?:\ -c(\d+))?(\ -n)?$' => [string=hello!] [count=2] <new_line>)]
```

You might also want to set the `usage` parameter of the `command()` function
decorator to display a alternative usage string, especially when using the
`RegExArgConverter.defaults` attribute.
