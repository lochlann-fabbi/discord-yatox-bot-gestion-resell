import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.message_content = True  # important pour clean

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- WEBHOOKS ----------
WEBHOOK_GOAL = "https://discord.com/api/webhooks/1463637934069776548/NKtbv5Fh1P8GoqVsRa6iNB6ZNUwBFNpFtsGeHMtIDqHvf5rWS2kqTsujy1DK3aVd1M2G"
WEBHOOK_IDEA = "https://discord.com/api/webhooks/1463640371740282912/mNvxChW37yDVhnIBAiFBpr1IT6lHs9VOgZaR6dd1L2LrLevztPsaw4n0CaLVoQRrR419"
WEBHOOK_PROBLEM = "https://discord.com/api/webhooks/1463639955736625174/C8e2rpKiG3EswPz_R-_jnk-QD3L8ooWZNedNR4-vjarIxFtSaSMrh_hh6iHNrdUDvZ5G"

# ---------- FONCTION ENVOI WEBHOOK ----------
async def send_webhook(url: str, embed: discord.Embed):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(url, session=session)
        await webhook.send(embed=embed)

# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user} !")
    synced = await bot.tree.sync()
    print(f"🔹 {len(synced)} commandes slash synchronisées.")

# ---------- COMMANDES ----------

@bot.tree.command(name="ping", description="Afficher le ping du bot")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 Pong !",
        description=f"Ping : {round(bot.latency * 1000)} ms",
        color=0x1abc9c
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="goal", description="Envoyer un objectif")
@app_commands.describe(text="Ton objectif")
async def goal(interaction: discord.Interaction, text: str):
    embed = discord.Embed(title="🎯 Objectif", description=text, color=0x3498db)
    await send_webhook(WEBHOOK_GOAL, embed)
    await interaction.response.send_message("✅ Objectif envoyé", ephemeral=True)

@bot.tree.command(name="idea", description="Proposer une idée")
@app_commands.describe(text="Ton idée")
async def idea(interaction: discord.Interaction, text: str):
    embed = discord.Embed(title="💡 Idée", description=text, color=0x9b59b6)
    await send_webhook(WEBHOOK_IDEA, embed)
    await interaction.response.send_message("✅ Idée envoyée", ephemeral=True)

@bot.tree.command(name="problem", description="Signaler un problème")
@app_commands.describe(text="Le problème")
async def problem(interaction: discord.Interaction, text: str):
    embed = discord.Embed(title="⚠️ Problème", description=text, color=0xe74c3c)
    await send_webhook(WEBHOOK_PROBLEM, embed)
    await interaction.response.send_message("✅ Problème envoyé", ephemeral=True)

@bot.tree.command(name="clean", description="Supprimer des messages")
@app_commands.describe(nombre="Nombre de messages à supprimer (max 100)")
async def clean(interaction: discord.Interaction, nombre: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Permission refusée", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=nombre)
    msg = await interaction.followup.send(f"🧹 {len(deleted)} messages supprimés")
    await asyncio.sleep(5)
    await msg.delete()

@bot.tree.command(name="embed", description="Créer un embed personnalisé")
@app_commands.describe(
    titre="Le titre de l'embed",
    description="La description de l'embed",
    image="URL d'une image (optionnel)"
)
async def embed_cmd(interaction: discord.Interaction, titre: str, description: str, image: str = None):
    embed = discord.Embed(title=titre, description=description, color=0x1abc9c)
    if image:
        embed.set_image(url=image)
    await interaction.response.send_message(embed=embed)

# ---------- RUN ----------
bot.run(os.getenv("DISCORD_TOKEN"))