import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

USER_ALVO = 716390085896962058

AMIGA_ID = 1115812841782517842
VOCE_ID = 1296916918728658980

CANAIS_MONITORADOS = {
    1498743327518884042, 1498743331079848006, 1498743334246682666,
    1498743337375498341, 1498743340924014835, 1498743344120201216,
    1498743347114803351, 1498743350399074424, 1498743353465114756,
    1498743357122416751, 1498743368098910409, 1498743371043307611,
    1498743374092566548, 1498743377414328380, 1498743380769898567,
    1498743384158769276, 1498743387342508154, 1498743390765056151,
    1498743394065977595, 1498743397249323051, 1498743400906883295,
    1498743404861853766, 1498743408431333520, 1498743411711414364,
    1498743415154802900, 1498743418564776038, 1498743421677076550,
    1498743424642191591, 1498743427754360913, 1498743431508398320,
    1498743434863710208, 1498743437925814364, 1498743441193177188,
    1498743444636569731, 1498743447736291411, 1498743451192397875,
    1498743454535254016, 1498743457542308002, 1498743460964991029,
    1498743464119238686, 1498743467231285398, 1498743470687260862,
    1498743473740709918, 1498743476735443004, 1498743480048943134,
    1498743483391934644, 1498743486831132733, 1498743490073595975,
    1498743493181575168, 1498743497023422657
}

# cache das DMs (mais rápido)
dm_cache = {}

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

    # já abre as DMs ao iniciar (evita delay depois)
    for uid in [AMIGA_ID, VOCE_ID]:
        user = await bot.fetch_user(uid)
        dm_cache[uid] = await user.create_dm()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id == USER_ALVO and message.channel.id in CANAIS_MONITORADOS:

        alerta = (
            f"🚨 ALERTA 🚨\n"
            f"Canal: {message.channel.name}\n"
            f"Mensagem: {message.content}"
        )

        # envia pra você
        try:
            await dm_cache[VOCE_ID].send(alerta)
        except Exception as e:
            print(f"Erro DM você: {e}")

        # envia pra sua amiga com mensagem extra ✨
        try:
            await dm_cache[AMIGA_ID].send(
                alerta + "\n\n💖 Você é a pessoa mais angelical do mundo 💖"
            )
        except Exception as e:
            print(f"Erro DM amiga: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
