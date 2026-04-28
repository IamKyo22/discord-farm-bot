import discord
from discord.ext import commands, tasks
import os
import io
import aiohttp
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs configurados
ALVOS_IDS = [716390085896962058, 854233015475109888]
AMIGA_ID = 1115812841782517842
VOCE_ID = 1296916918728658980

CANAIS_MONITORADOS = [
    1498743327518884042, 1498743331079848006, 1498743334246682666,
    1498743337375498341, 1498743340924014835, 1498743344120201216,
    1498743347114803351, 1498743350399074424, 1498743353465114756,
    1498743357122416751, 1498743368098910409, 1498743371043307611,
    1498743340924014835, 1498743344120201216, 1498743347114803351,
    1498743350399074424, 1498743353465114756, 1498743357122416751,
    1498743368098910409, 1498743371043307611, 1498743374092566548, 
    1498743377414328380, 1498743380769898567, 1498743384158769276, 
    1498743387342508154, 1498743390765056151, 1498743394065977595, 
    1498743397249323051, 1498743400906883295, 1498743404861853766, 
    1498743408431333520, 1498743411711414364, 1498743415154802900, 
    1498743418564776038, 1498743421677076550, 1498743424642191591, 
    1498743427754360913, 1498743431508398320, 1498743434863710208, 
    1498743437925814364, 1498743441193177188, 1498743444636569731, 
    1498743447736291411, 1498743451192397875, 1498743454535254016, 
    1498743457542308002, 1498743460964991029, 1498743464119238686, 
    1498743467231285398, 1498743470687260862, 1498743473740709918, 
    1498743476735443004, 1498743480048943134, 1498743483391934644, 
    1498743486831132733, 1498743490073595975, 1498743493181575168, 
    1498743497023422657
]

mensagens_vistas = set()
dm_cache = {}

async def download_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.read()
    except:
        return None

async def enviar_alerta(message):
    # Identifica se é o bot de Pokémon ou o usuário alvo
    is_poke_bot = message.author.id == 854233015475109888
    
    # Título e Cor baseada em quem enviou
    titulo = "⚡ Pokémon Detectado!" if is_poke_bot else "🔔 Novo Alerta"
    cor = 0xff0000 if is_poke_bot else 0x00ff00 # Vermelho para Pokémon, Verde para usuário
    
    embed = discord.Embed(
        title=titulo,
        description=f"**Canal:** {message.channel.mention}\n**Link:** [Clique aqui]({message.jump_url})",
        color=cor,
        timestamp=datetime.now()
    )

    conteudo_extra = message.content if message.content else ""
    if conteudo_extra:
        embed.add_field(name="💬 Mensagem", value=conteudo_extra, inline=False)

    arquivo_final = None
    url_img = None

    # Tenta pegar a imagem se houver embed (caso do Bot)
    if message.embeds:
        original_embed = message.embeds[0]
        # Se o bot mandou informação no embed, a gente copia para o nosso
        if original_embed.title: embed.add_field(name="📌 Info", value=original_embed.title)
        if original_embed.description: embed.description += f"\n\n{original_embed.description}"
        
        # Prioridade para a foto do Pokémon
        if original_embed.image.url: url_img = original_embed.image.url
        elif original_embed.thumbnail.url: url_img = original_embed.thumbnail.url

    # Se não tinha no embed, tenta ver se é anexo (upload direto)
    if not url_img and message.attachments:
        url_img = message.attachments[0].url

    # Se achamos uma imagem, baixamos para colocar DENTRO do embed
    if url_img:
        img_data = await download_image(url_img)
        if img_data:
            arquivo_final = discord.File(io.BytesIO(img_data), filename="pokemon.png")
            embed.set_image(url="attachment://pokemon.png")

    # --- ENVIO ---
    async def disparar(target_id, prefixo=""):
        # Criamos uma cópia do arquivo e do embed para cada envio
        file_copy = discord.File(io.BytesIO(img_data), filename="pokemon.png") if arquivo_final else None
        try:
            await dm_cache[target_id].send(content=prefixo, embed=embed, file=file_copy)
        except Exception as e:
            print(f"Erro ao enviar para {target_id}: {e}")

    # Envia para você
    await disparar(VOCE_ID)
    
    # Envia para sua amiga com a mensagem especial
    msg_amiga = "💖 **Yori:** Você é a pessoa mais especial e angelical que ja vi, tsu."
    await disparar(AMIGA_ID, prefixo=msg_amiga)

@bot.event
async def on_ready():
    print(f"🤖 Monitor ligado: {bot.user}")
    for uid in [AMIGA_ID, VOCE_ID]:
        try:
            user = await bot.fetch_user(uid)
            dm_cache[uid] = await user.create_dm()
        except: pass
    check_recent.start()

@bot.event
async def on_message(message):
    if message.author.id in ALVOS_IDS and message.channel.id in CANAIS_MONITORADOS:
        if message.id not in mensagens_vistas:
            mensagens_vistas.add(message.id)
            await enviar_alerta(message)
    await bot.process_commands(message)

@tasks.loop(seconds=10)
async def check_recent():
    for guild in bot.guilds:
        for channel_id in CANAIS_MONITORADOS:
            channel = guild.get_channel(channel_id)
            if not channel: continue
            try:
                async for msg in channel.history(limit=10):
                    if (msg.author.id in ALVOS_IDS and 
                        msg.id not in mensagens_vistas and 
                        (datetime.now(timezone.utc) - msg.created_at).total_seconds() < 300):
                        mensagens_vistas.add(msg.id)
                        await enviar_alerta(msg)
            except: pass

bot.run(TOKEN)
