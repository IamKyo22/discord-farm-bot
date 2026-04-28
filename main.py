import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logado como {bot.user}')

@bot.command()
async def ids(ctx):
    try:
        guild = ctx.guild

        # pega a categoria
        category = discord.utils.get(guild.categories, id=1498743325526855762)

        if not category:
            return await ctx.send("Categoria não encontrada 💀")

        canais_ids = [str(channel.id) for channel in category.channels]

        resultado = " ".join(canais_ids)

        # pega canal onde vai enviar
        canal_envio = guild.get_channel(1286477337311051778)

        if not canal_envio:
            return await ctx.send("Canal de envio não encontrado 💀")

        # divide se passar de 2000 chars
        if len(resultado) > 2000:
            partes = [resultado[i:i+1900] for i in range(0, len(resultado), 1900)]
            for parte in partes:
                await canal_envio.send(parte)
        else:
            await canal_envio.send(resultado)

        await ctx.send("IDs enviados com sucesso 😈")

    except Exception as e:
        print(f"ERRO: {e}")
        await ctx.send(f"Erro: {e}")

if not TOKEN:
    print("ERRO: TOKEN não encontrado!")
else:
    bot.run(TOKEN)
