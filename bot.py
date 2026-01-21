import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync globale (peut prendre jusqu'à 1h, mais OK après)
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")

# Slash command TEST
@bot.tree.command(name="ping", description="Tester si le bot fonctionne")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong ! Le bot fonctionne.")

bot.run(os.getenv("DISCORD_TOKEN"))