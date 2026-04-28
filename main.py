import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

USER_ALVO = 716390085896962058

USUARIOS_ALERTA = [
    1115812841782517842,
    1296916918728658980
]

CANAIS_MONITORADOS = {
    1498743327518884042, 1498743331079848006, 1498743334246682666,
    1498743337375498341, 1498743340924014835, 1498743344120201216
}

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id == USER_ALVO and message.channel.id in CANAIS_MONITORADOS:

        for user_id in USUARIOS_ALERTA:
            try:
                user = bot.get_user(user_id)

                # se não estiver em cache, busca
                if user is None:
                    user = await bot.fetch_user(user_id)

                await user.send(
                    f"🚨 ALERTA 🚨\n"
                    f"Canal: {message.channel.name}\n"
                    f"Mensagem: {message.content}"
                )

                print(f"Enviado para {user_id}")

            except Exception as e:
                print(f"Erro ao enviar DM para {user_id}: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
