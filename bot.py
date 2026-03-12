import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_GOAL_ID = int(os.getenv("CHANNEL_GOAL", 0))
CHANNEL_IDEA_ID = int(os.getenv("CHANNEL_IDEA", 0))
CHANNEL_PROBLEM_ID = int(os.getenv("CHANNEL_PROBLEM", 0))

TABLES_FILE = "tables.json"
ITEMS_PER_PAGE = 15
TAX_RATE = 0.072

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- UTILS ---
def load_tables():
    if not os.path.exists(TABLES_FILE): return {}
    with open(TABLES_FILE, "r", encoding="utf-8") as f: return json.load(f).get("tables", {})

def save_tables(data):
    with open(TABLES_FILE, "w", encoding="utf-8") as f: json.dump({"tables": data}, f, indent=2, ensure_ascii=False)

def calculate_totals(table):
    items = table["items"]
    v_count = sum(1 for i in items if i["status"].upper() == "VENDU")
    ca = sum(float(i.get("prix", 0)) for i in items if i["status"].upper() == "VENDU")
    p_achat = float(table["prix_achat"])
    return round(ca, 2), round(ca - p_achat, 2), round((ca * (1 - TAX_RATE)) - p_achat, 2), v_count, len(items)

def build_table_embeds(table_id):
    tables = load_tables()
    if table_id not in tables: return []
    table = tables[table_id]
    ca, b_brut, b_net, v_count, t_count = calculate_totals(table)
    pages = []
    for i in range(0, len(table["items"]), ITEMS_PER_PAGE):
        e = discord.Embed(title=f"📦 {table['name']}", description=f"📊 Ventes: **`{v_count}/{t_count}`**\n💰 Achat: `{table['prix_achat']}€` | 📈 CA: `{ca}€`\n📈 Brut: `{b_brut}€` | 👛 Net: **`{b_net}€`**", color=0x2ECC71)
        e.set_thumbnail(url=table.get("image", "https://i.ibb.co/5gt93MmG/The-North-Face-Logo.jpg"))
        for idx, it in enumerate(table["items"][i:i + ITEMS_PER_PAGE], start=i + 1):
            st = it["status"].upper()
            emo = "✅" if st == "VENDU" else "⚠️" if st == "PROBLEME" else "⏳"
            lnk = f"| [🔗 Voir]({it['url']})" if it.get('url') and it['url'] != "#" else "| ❌ Pas de lien"
            e.add_field(name=f"{emo} {idx}. {it['nom']}", value=f"💸 `{it.get('prix', 0)}€` | 📄 `{it['status']}` {lnk}", inline=False)
        e.set_footer(text=f"Page {len(pages)+1}/{(len(table['items'])-1)//ITEMS_PER_PAGE+1} • ID: {table_id}")
        pages.append(e)
    return pages

# --- MODALS & VIEWS ---
class BaseModal(discord.ui.Modal):
    index = discord.ui.TextInput(label="Index", placeholder="Ex: 1")
    def __init__(self, view, title, label, attr):
        super().__init__(title=title); self.view, self.attr = view, attr
        self.input = discord.ui.TextInput(label=label); self.add_item(self.input)
    async def on_submit(self, i):
        tables = load_tables(); idx = int(self.index.value) - 1
        val = self.input.value
        if self.attr == "prix": val = float(val.replace(',', '.'))
        elif self.attr == "status": val = val.upper()
        tables[self.view.table_id]["items"][idx][self.attr] = val
        save_tables(tables); await self.view.refresh_embeds()
        await i.response.edit_message(embed=self.view.embeds[self.view.index], view=self.view)

class TablePaginator(discord.ui.View):
    def __init__(self, table_id):
        super().__init__(timeout=None); self.table_id = table_id
        for b in self.children: b.custom_id = f"table:{b.label.lower()}:{table_id}"
        self.embeds = build_table_embeds(table_id); self.index = 0
    async def refresh_embeds(self): self.embeds = build_table_embeds(self.table_id)
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, i, b): self.index = (self.index-1)%len(self.embeds); await i.response.edit_message(embed=self.embeds[self.index])
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, i, b): self.index = (self.index+1)%len(self.embeds); await i.response.edit_message(embed=self.embeds[self.index])
    @discord.ui.button(label="Nom 🔤", style=discord.ButtonStyle.primary)
    async def ed_name(self, i, b): await i.response.send_modal(BaseModal(self, "Nom", "Nouveau nom", "nom"))
    @discord.ui.button(label="Prix 💸", style=discord.ButtonStyle.primary)
    async def ed_price(self, i, b): await i.response.send_modal(BaseModal(self, "Prix", "Prix (€)", "prix"))
    @discord.ui.button(label="Status 📄", style=discord.ButtonStyle.primary)
    async def ed_status(self, i, b): await i.response.send_modal(BaseModal(self, "Statut", "VENDU/EN VENTE", "status"))
    @discord.ui.button(label="Lien 🔗", style=discord.ButtonStyle.secondary)
    async def ed_url(self, i, b): await i.response.send_modal(BaseModal(self, "Lien", "URL", "url"))

# --- TASK VIEWS ---
class GoalView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Objectif Atteint 🏆", style=discord.ButtonStyle.success, custom_id="goal_v9")
    async def done(self, i, b):
        e = i.message.embeds[0]; e.title = "✅ Objectif Terminé"; e.color = 0xF1C40F
        e.add_field(name="Fait par", value=i.user.mention); await i.response.edit_message(embed=e, view=None)

class IdeaView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Adopter l'idée 🚀", style=discord.ButtonStyle.primary, custom_id="idea_v9")
    async def adopt(self, i, b):
        e = i.message.embeds[0]; e.title = "🔥 Idée en cours"; e.color = 0x9B59B6
        nv = discord.ui.View(timeout=None); btn = discord.ui.Button(label="Mise en place ✅", style=discord.ButtonStyle.success, custom_id="idea_fin_v9")
        async def fin(i2): e.title = "💎 Idée Appliquée"; await i2.response.edit_message(embed=e, view=None)
        btn.callback = fin; nv.add_item(btn); await i.response.edit_message(embed=e, view=nv)

class ProbView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Problème Résolu ✅", style=discord.ButtonStyle.success, custom_id="prob_v9")
    async def solved(self, i, b):
        e = i.message.embeds[0]; e.title = "🟢 Résolu"; e.color = 0x2ECC71
        e.add_field(name="Par", value=i.user.mention); await i.response.edit_message(embed=e, view=None)

class TaskModal(discord.ui.Modal):
    def __init__(self, title, cid, v_type):
        super().__init__(title=title); self.cid, self.v_type = cid, v_type
        self.txt = discord.ui.TextInput(label="Détail", style=discord.TextStyle.paragraph); self.add_item(self.txt)
    async def on_submit(self, i):
        c = bot.get_channel(self.cid)
        e = discord.Embed(description=self.txt.value); e.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
        if self.v_type == "goal": e.title, e.color, v = "🎯 Objectif", 0x3498DB, GoalView()
        elif self.v_type == "idea": e.title, e.color, v = "💡 Idée", 0xF1C40F, IdeaView()
        else: e.title, e.color, v = "🚨 Problème", 0xE74C3C, ProbView()
        await c.send(embed=e, view=v); await i.response.send_message("✅", ephemeral=True)

# --- COMMANDS ---
@bot.tree.command(name="ping")
async def ping(i): await i.response.send_message(f"🏓 **{round(bot.latency*1000)}ms**")

@bot.tree.command(name="clean")
async def clean(i, nombre: int):
    if not i.user.guild_permissions.manage_messages: return await i.response.send_message("❌", ephemeral=True)
    await i.response.defer(ephemeral=True); await i.channel.purge(limit=nombre)
    await i.followup.send(f"🗑️ **{nombre}** messages nettoyés.")

@bot.tree.command(name="goal")
async def goal(i): await i.response.send_modal(TaskModal("🎯 Objectif", CHANNEL_GOAL_ID, "goal"))

@bot.tree.command(name="idea")
async def idea(i): await i.response.send_modal(TaskModal("💡 Idée", CHANNEL_IDEA_ID, "idea"))

@bot.tree.command(name="problem")
async def problem(i): await i.response.send_modal(TaskModal("🚨 Problème", CHANNEL_PROBLEM_ID, "problem"))

async def table_autocomp(i, cur):
    return [app_commands.Choice(name=d["name"], value=t) for t, d in load_tables().items() if cur.lower() in d["name"].lower()][:25]

@bot.tree.command(name="table_show")
@app_commands.autocomplete(table_id=table_autocomp)
async def table_show(i, table_id: str):
    v = TablePaginator(table_id)
    if not v.embeds: return await i.response.send_message("❌", ephemeral=True)
    await i.response.send_message(embed=v.embeds[0], view=v)

@bot.tree.command(name="refresh_views")
async def refresh(i):
    for t in load_tables(): bot.add_view(TablePaginator(t))
    for v in [GoalView(), IdeaView(), ProbView()]: bot.add_view(v)
    await i.response.send_message("✅", ephemeral=True)

@bot.event
async def on_ready():
    for v in [GoalView(), IdeaView(), ProbView()]: bot.add_view(v)
    for t in load_tables(): bot.add_view(TablePaginator(t))
    await bot.tree.sync(); print(f"✅ {bot.user}")

bot.run(DISCORD_TOKEN)
