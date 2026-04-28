import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logado como {bot.user}')

@bot.command(name="chanell")
@commands.has_permissions(administrator=True)
async def create_farm(ctx):
    guild = ctx.guild

    # cria categoria
    category = await guild.create_category("🌿 farm")

    canais_ids = []

    for i in range(1, 91):
        channel = await guild.create_text_channel(
            f"farm-{i} 🌿",
            category=category
        )
        canais_ids.append(str(channel.id))

        await asyncio.sleep(0.5)  # anti rate limit

    # monta comando completo
    resultado = "@poketwo redirect " + " ".join(canais_ids)

    print(resultado)

    # manda no chat (pode ser grande, então quebra se precisar)
    if len(resultado) > 2000:
        partes = [resultado[i:i+1900] for i in range(0, len(resultado), 1900)]
        for parte in partes:
            await ctx.send(parte)
    else:
        await ctx.send(resultado)

    await ctx.send("🌿 Farm criada + redirect pronto!")

bot.run(TOKEN)
