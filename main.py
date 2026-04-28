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
async def create_farm(ctx):
    try:
        if ctx.guild is None:
            return await ctx.send("Usa isso em um servidor.")

        # cria categoria
        category = await ctx.guild.create_category("🌿 farm")

        canais_ids = []

        for i in range(1, 91):
            channel = await ctx.guild.create_text_channel(
                f"farm-{i} 🌿",
                category=category
            )
            canais_ids.append(str(channel.id))
            await asyncio.sleep(0.5)

        resultado = "@poketwo redirect " + " ".join(canais_ids)

        print(resultado)

        # evita limite de 2000 chars
        if len(resultado) > 2000:
            partes = [resultado[i:i+1900] for i in range(0, len(resultado), 1900)]
            for parte in partes:
                await ctx.send(parte)
        else:
            await ctx.send(resultado)

        await ctx.send("🌿 Farm criada + redirect pronto!")

    except Exception as e:
        await ctx.send(f"Erro: {e}")
        print(f"ERRO: {e}")


# proteção contra token vazio
if not TOKEN:
    print("ERRO: TOKEN não encontrado nas variáveis!")
else:
    bot.run(TOKEN)
