import discord
from discord.ext import commands, tasks
import os
import io
import aiohttp # Necessário para baixar imagens de links de embeds
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configurações de IDs
USER_ALVO = 716390085896962058
AMIGA_ID = 1115812841782517842
VOCE_ID = 1296916918728658980

CANAIS_MONITORADOS = [
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
]

mensagens_vistas = set()
dm_cache = {}

# --- FUNÇÃO PARA PEGAR IMAGEM DE URL (EMBEDS) ---
async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

# --- FUNÇÃO PRINCIPAL DE ALERTA ---
async def enviar_alerta(message):
    # Criando o Embed de decoração
    embed_base = discord.Embed(
        title="✨ Novo Alerta Detectado! ✨",
        description=f"**Canal:** {message.channel.mention}\n**Autor:** `{message.author}`",
        color=0xff69b4, # Cor rosa/pink
        timestamp=datetime.now()
    )
    
    conteudo_texto = message.content if message.content else ""
    
    # Se a mensagem original tiver embeds (ex: bot de pokemon)
    embeds_copiados = []
    lista_urls_imagens = []

    if message.embeds:
        for emb in message.embeds:
            # Copia o embed original para manter a formatação do bot alvo
            novo_emb = emb.copy()
            embeds_copiados.append(novo_emb)
            # Tenta pegar a imagem do embed
            if emb.image.url: lista_urls_imagens.append(emb.image.url)
            if emb.thumbnail.url: lista_urls_imagens.append(emb.thumbnail.url)

    # Preparando arquivos (Attachments + Imagens de Embeds)
    arquivos_finais = []
    
    # 1. Processa anexos comuns
    if message.attachments:
        for anexo in message.attachments:
            b = await anexo.read()
            arquivos_finais.append((b, anexo.filename))

    # 2. Processa imagens que estavam dentro de embeds
    for url in lista_urls_imagens:
        img_bytes = await download_image(url)
        if img_bytes:
            arquivos_finais.append((img_bytes, "pokemon_image.png"))

    # Montando as listas de arquivos para cada envio (evitar conflito de IO)
    def gerar_files():
        return [discord.File(io.BytesIO(b), filename=f) for b, f in arquivos_finais]

    # --- ENVIO PARA VOCÊ ---
    try:
        await dm_cache[VOCE_ID].send(
            content=f"🔗 [Ir para mensagem]({message.jump_url})\n{conteudo_texto}",
            embeds=[embed_base] + embeds_copiados,
            files=gerar_files()
        )
    except Exception as e:
        print(f"Erro ao enviar para Você: {e}")

    # --- ENVIO PARA AMIGA ---
    try:
        msg_especial = "💖 **Yori:** Você é a pessoa mais especial e angelical que ja vi, tsu."
        await dm_cache[AMIGA_ID].send(
            content=f"{msg_especial}\n🔗 [Mensagem original]({message.jump_url})\n{conteudo_texto}",
            embeds=[embed_base] + embeds_copiados,
            files=gerar_files()
        )
    except Exception as e:
        print(f"Erro ao enviar para Amiga: {e}")

# --- RESTANTE DO CÓDIGO (EVENTOS E LOOP) ---

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    for uid in [AMIGA_ID, VOCE_ID]:
        try:
            user = await bot.fetch_user(uid)
            dm_cache[uid] = await user.create_dm()
        except:
            print(f"❌ Não consegui abrir DM com {uid}")
    check_recent.start()

@bot.event
async def on_message(message):
    if message.author.bot and message.author.id != USER_ALVO: # Ignora outros bots, mas aceita se o alvo for bot
        return
    if message.author.id == USER_ALVO and message.channel.id in CANAIS_MONITORADOS:
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
                async for msg in channel.history(limit=20):
                    if (msg.author.id == USER_ALVO and 
                        msg.id not in mensagens_vistas and 
                        (datetime.now(timezone.utc) - msg.created_at).total_seconds() < 300):
                        mensagens_vistas.add(msg.id)
                        await enviar_alerta(msg)
            except:
                pass

bot.run(TOKEN)
