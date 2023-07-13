from discord import (
    Client as DiscordClient,
    Embed,
    Intents as ClientIntents,
    Message,
)

from src.config import Settings
from src.translator import Translator


def needs_translation_reply(original_text: str, translated_text: str) -> bool:
    return original_text != translated_text


def _register_client_events(client: DiscordClient, translator: Translator):
    @client.event
    async def on_message(msg: Message):
        if msg.author == client.user or msg.author.bot:
            return

        if not msg.content or msg.content.startswith("!"):
            return

        translated_text = translator.translate(msg.content)
        if needs_translation_reply(msg.clean_content, translated_text):
            await msg.reply(
                embed=Embed(description=translated_text, color=0x00FFFF),
                mention_author=False,
                silent=True,
            )

    @client.event
    async def on_message_edit(before: Message, after: Message):
        if before.content == after.content:
            return

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
                    translated_text = translator.translate(after.content)
                    if needs_translation_reply(after.clean_content, translated_text):
                        await m.edit(
                            content=None,
                            embed=Embed(description=translated_text, color=0x00FFFF),
                        )

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
    _register_client_events(
        client, translator=Translator(project_id=settings.GOOGLE_PROJECT_ID)
    )
    client.run(token=settings.DISCORD_TOKEN, reconnect=True)
