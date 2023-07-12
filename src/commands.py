from random import choice as random_choice

from discord.ext.commands import Bot


__all__ = ["register_bot_commands"]


async def _nine_nine(ctx):
    brooklyn_99_quotes = [
        "I'm the human form of the 💯 emoji.",
        "Bingpot!",
        (
            "Cool. Cool cool cool cool cool cool cool, "
            "no doubt no doubt no doubt no doubt."
        ),
    ]

    response = random_choice(brooklyn_99_quotes)
    await ctx.send(response)


def register_bot_commands(bot: Bot):
    # bot.add_command(
    #     Command(
    #         name="99",
    #         help="Responds with a random quote from Brooklyn 99",
    #         func=_nine_nine,
    #     )
    # )
    ...
