import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Webhooks
WEBHOOK_GOAL = "https://discord.com/api/webhooks/1463637934069776548/NKtbv5Fh1P8GoqVsRa6iNB6ZNUwBFNpFtsGeHMtIDqHvf5rWS2kqTsujy1DK3aVd1M2G"
WEBHOOK_IDEA = "https://discord.com/api/webhooks/1463640371740282912/mNvxChW37yDVhnIBAiFBpr1IT6lHs9VOgZaR6dd1L2LrLevztPsaw4n0CaLVoQRrR419"
WEBHOOK_PROBLEM = "https://discord.com/api/webhooks/1463639955736625174/C8e2rpKiG3EswPz_R-_jnk-QD3L8ooWZNedNR4-vjarIxFtSaSMrh_hh6iHNrdUDvZ5G"


async def send_webhook(webhook_url: str, embed: discord.Embed):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)


@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user} !")
    try:
        synced = await bot.tree.sync()
        print(f"🔹 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print("Erreur lors de la synchronisation des slash commands:", e)


# /ping
@bot.tree.command(name="ping", description="Affiche le ping du bot")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"Ping : {round(bot.latency * 1000)}ms",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)


# /goal
@bot.tree.command(name="goal", description="Envoie un objectif")
@app_commands.describe(text="L'objectif à envoyer")
async def goal(interaction: discord.Interaction, text: str):
    embed = discord.Embed(
        title="🎯 Objectif",
        description=text,
        color=discord.Color.blue()
    )
    await send_webhook(WEBHOOK_GOAL, embed)
    await interaction.response.send_message(f"Objectif envoyé ! ✅", ephemeral=True)


# /idea
@bot.tree.command(name="idea", description="Propose une idée")
@app_commands.describe(text="L'idée à envoyer")
async def idea(interaction: discord.Interaction, text: str):
    embed = discord.Embed(
        title="💡 Nouvelle idée",
        description=text,
        color=discord.Color.purple()
    )
    await send_webhook(WEBHOOK_IDEA, embed)
    await interaction.response.send_message(f"Idée envoyée ! ✅", ephemeral=True)


# /problem
@bot.tree.command(name="problem", description="Signale un problème")
@app_commands.describe(text="Le problème à signaler")
async def problem(interaction: discord.Interaction, text: str):
    embed = discord.Embed(
        title="⚠️ Problème",
        description=text,
        color=discord.Color.red()
    )
    await send_webhook(WEBHOOK_PROBLEM, embed)
    await interaction.response.send_message(f"Problème signalé ! ✅", ephemeral=True)


bot.run(os.getenv("DISCORD_TOKEN"))
