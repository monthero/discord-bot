from discord import (
    Client as DiscordClient,
    Intents as ClientIntents,
    Message,
)

from src.config import Settings
from src.translator import Translator


def run_discord_bot():
    settings = Settings()

    INTENTS = ClientIntents.default()
    INTENTS.members = True
    INTENTS.messages = True
    INTENTS.message_content = True
    INTENTS.guilds = True
    INTENTS.reactions = True
    INTENTS.typing = False
    INTENTS.presences = False
    INTENTS.voice_states = False
    INTENTS.invites = False
    INTENTS.webhooks = False

    client = DiscordClient(intents=INTENTS)
    translator = Translator(project_id=settings.GOOGLE_PROJECT_ID)

    @client.event
    async def on_ready():
        # _guild = discord_utils.get(client.guilds, name=settings.DISCORD_SERVER_NAME)
        ...

    @client.event
    async def on_message(msg: Message):
        if msg.author == client.user or msg.author.bot:
            return

        if not msg.content or msg.content.startswith("!"):
            return

        await msg.channel.send(translator.translate(msg.content), reference=msg)
        # await msg.channel.purge(limit=None)

    @client.event
    async def on_message_edit(before: Message, after: Message):
        if before.author == client.user or before.author.bot:
            return

        async for m in before.channel.history(limit=200):
            if (
                m.reference
                and m.reference.message_id == before.id
                and m.author == client.user
            ):
                if not after.content or after.content.startswith("!"):
                    await m.delete()
                else:
                    await m.edit(content=translator.translate(after.content))

    @client.event
    async def on_message_delete(msg: Message):
        """Deletes all bot replies to the deleted message"""

        if msg.author == client.user or msg.author.bot:
            return

        async for m in msg.channel.history(limit=200):
            if (
                m.reference
                and m.reference.message_id == msg.id
                and m.author == client.user
            ):
                await m.delete()

    client.run(
        token=settings.DISCORD_TOKEN,
        # reconnect=True,
    )
