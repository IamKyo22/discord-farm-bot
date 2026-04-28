import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

USER_ALVO = 716390085896962058

AMIGA_ID = 1115812841782517842
VOCE_ID = 1296916918728658980

CANAIS_MONITORADOS = [
    1498743327518884042, 1498743331079848006, 1498743334246682666,
    1498743337375498341, 1498743340924014835, 1498743344120201216
]

mensagens_vistas = set()
dm_cache = {}

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

    for uid in [AMIGA_ID, VOCE_ID]:
        user = await bot.fetch_user(uid)
        dm_cache[uid] = await user.create_dm()

    check_recent.start()

# 🔴 tempo real
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id == USER_ALVO and message.channel.id in CANAIS_MONITORADOS:
        if message.id not in mensagens_vistas:
            mensagens_vistas.add(message.id)
            await enviar_alerta(message)

    await bot.process_commands(message)

# 🟡 varredura últimos 5 min
@tasks.loop(seconds=10)
async def check_recent():
    for guild in bot.guilds:
        for channel_id in CANAIS_MONITORADOS:
            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            try:
                async for msg in channel.history(limit=50):
                    if (
                        msg.author.id == USER_ALVO and
                        msg.id not in mensagens_vistas and
                        datetime.now(timezone.utc) - msg.created_at < timedelta(minutes=5)
                    ):
                        mensagens_vistas.add(msg.id)
                        await enviar_alerta(msg)

            except Exception as e:
                print(f"Erro ao varrer: {e}")

# 🚨 envio
async def enviar_alerta(message):
    alerta = (
        f"🚨 ALERTA 🚨\n"
        f"Canal: {message.channel.name}\n"
        f"Mensagem: {message.content}"
    )

    try:
        await dm_cache[VOCE_ID].send(alerta)
    except Exception as e:
        print(f"Erro você: {e}")

    try:
        await dm_cache[AMIGA_ID].send(
            alerta + "\n\n💖 Você é a pessoa mais angelical do mundo 💖"
        )
    except Exception as e:
        print(f"Erro amiga: {e}")

bot.run(TOKEN)
