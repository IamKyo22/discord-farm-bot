import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True  # necessário pra pegar usuários

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs
USER_ALVO = 716390085896962058

USUARIOS_ALERTA = [
    1115812841782517842,  # sua amiga
    1296916918728658980   # você
]

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

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # verifica se é o usuário alvo nos canais certos
    if message.author.id == USER_ALVO and message.channel.id in CANAIS_MONITORADOS:

        for user_id in USUARIOS_ALERTA:
            try:
                user = await bot.fetch_user(user_id)
                await user.send(
                    f"🚨 ALERTA 🚨\n"
                    f"O usuário falou em {message.channel.mention}\n"
                    f"Mensagem: {message.content}"
                )
            except Exception as e:
                print(f"Erro ao enviar DM: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
