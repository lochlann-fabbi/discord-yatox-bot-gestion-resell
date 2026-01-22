import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Chargement du .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Webhooks
WEBHOOK_GOAL = "https://discord.com/api/webhooks/1463637934069776548/NKtbv5Fh1P8GoqVsRa6iNB6ZNUwBFNpFtsGeHMtIDqHvf5rWS2kqTsujy1DK3aVd1M2G"
WEBHOOK_IDEA = "https://discord.com/api/webhooks/1463640371740282912/mNvxChW37yDVhnIBAiFBpr1IT6lHs9VOgZaR6dd1L2LrLevztPsaw4n0CaLVoQRrR419"
WEBHOOK_PROBLEM = "https://discord.com/api/webhooks/1463639955736625174/C8e2rpKiG3EswPz_R-_jnk-QD3L8ooWZNedNR4-vjarIxFtSaSMrh_hh6iHNrdUDvZ5G"

# Intents
intents = discord.Intents.default()
intents.message_content = True  # nécessaire si tu veux lire le contenu des messages

bot = commands.Bot(command_prefix="!", intents=intents)

# Synchronisation des commandes slash
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot connecté : {bot.user} !")
    print(f"🔹 {len(bot.tree.get_commands())} commandes slash synchronisées.")


# --------------------
# Commandes slash
# --------------------

# /ping
@bot.tree.command(name="ping", description="Affiche le ping du bot")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"Ping du bot : {round(bot.latency * 1000)} ms",
        color=0x00FFFF
    )
    await interaction.response.send_message(embed=embed)

# /goal
@bot.tree.command(name="goal", description="Envoyer un objectif")
@app_commands.describe(texte="Le texte de l'objectif")
async def goal(interaction: discord.Interaction, texte: str):
    embed = discord.Embed(
        title="🎯 Nouvel objectif",
        description=texte,
        color=0x1ABC9C
    )
    webhook = discord.Webhook.from_url(WEBHOOK_GOAL, session=discord.RequestsWebhookAdapter())
    webhook.send(embed=embed)
    await interaction.response.send_message("✅ Objectif envoyé !", ephemeral=True)

# /idea
@bot.tree.command(name="idea", description="Envoyer une idée")
@app_commands.describe(texte="Le texte de l'idée")
async def idea(interaction: discord.Interaction, texte: str):
    embed = discord.Embed(
        title="💡 Nouvelle idée",
        description=texte,
        color=0xF1C40F
    )
    webhook = discord.Webhook.from_url(WEBHOOK_IDEA, session=discord.RequestsWebhookAdapter())
    webhook.send(embed=embed)
    await interaction.response.send_message("✅ Idée envoyée !", ephemeral=True)

# /problem
@bot.tree.command(name="problem", description="Envoyer un problème")
@app_commands.describe(texte="Le texte du problème")
async def problem(interaction: discord.Interaction, texte: str):
    embed = discord.Embed(
        title="⚠️ Nouveau problème",
        description=texte,
        color=0xE74C3C
    )
    webhook = discord.Webhook.from_url(WEBHOOK_PROBLEM, session=discord.RequestsWebhookAdapter())
    webhook.send(embed=embed)
    await interaction.response.send_message("✅ Problème envoyé !", ephemeral=True)

# /clean
@bot.tree.command(name="clean", description="Supprime un nombre de messages")
@app_commands.describe(nombre="Nombre de messages à supprimer")
async def clean(interaction: discord.Interaction, nombre: int):
    # Répond immédiatement pour éviter le timeout
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=nombre)
    await interaction.followup.send(f"✅ Nettoyage terminé ! {len(deleted)} messages supprimés", ephemeral=True)

# --------------------
# Lancement du bot
# --------------------
bot.run(TOKEN)