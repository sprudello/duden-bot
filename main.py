from typing import Final
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import duden

from responses import get_response
from duden_scrape import get_wort_des_tages

# Load token from .env
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Needed to iterate over servers
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"[SYNCED] Logged in as {bot.user}")
    post_wort_des_tages.start()

@bot.tree.command(name="say", description="Bot responds with a message based on your input")
async def say(interaction: discord.Interaction, input: str):
    response = get_response(input)
    await interaction.response.send_message(response)

@bot.tree.command(name="word", description="Gives you the definition of a word in the Duden")
async def word(interaction: discord.Interaction, input: str):
    word = duden.get(str)
    await interaction.response.send_message(f"""
    Wort: {word.title}
    Aussprache: {word.phonetic}
    Wortart: {word.part_of_speech}
    Wortfrequenz: {word.frequency} von 5
    Nutzung: {word.usage}
    Worttrennung {word.word_separation}
    Bedeutung: {word.meaning_overview}
    Synonyme: {word.synonyms}
    Herkunft: {word.origin}
    Beispiele: {word.examples}
    Grammatik: {word.grammar_overview}
    Aussprache: {word.pronunciation_audio_url}
    """)

class DudenGroup(app_commands.Group):
    @app_commands.command(name="daily", description="Zeigt das heutige Wort des Tages an")
    async def daily(self, interaction: discord.Interaction):
        wort = get_wort_des_tages()
        if wort:
            title, link = wort.split(": ", 1)
            embed = discord.Embed(
                title=f"Wort des Tages: {title}",
                url=link,
                description="Klicke auf den Titel für mehr Infos 🔍",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Kein Wort des Tages verfügbar. Vielleicht schläft die deutsche Sprache noch.")

bot.tree.add_command(DudenGroup(name="duden", description="Duden Funktionen"))


@tasks.loop(minutes=60)
async def post_wort_des_tages():
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    if now.hour != 6:
        return  # Skip unless it's 6am

    wort = get_wort_des_tages()
    if not wort:
        wort = "Kein neues Wort heute. Sprache pausiert."

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name.lower() == "duden":
                try:
                    if ": " in wort:
                        title, link = wort.split(": ", 1)
                        embed = discord.Embed(
                        title=f"Guten Morgen! 🌞 Wort des Tages: {title}",
                        url=link,
                        description="Mehr Infos durch Klicken auf den Titel.",
                        color=discord.Color.gold()
                    )
                        await channel.send(embed=embed)
                    else:
                        await channel.send(wort)
                        print(f"✅ Posted in #{channel.name} on {guild.name}")
                        break  # Only post in the first valid #duden per server
                except Exception as e:
                    print(f"❌ Could not post in {guild.name} #{channel.name}: {e}")

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
