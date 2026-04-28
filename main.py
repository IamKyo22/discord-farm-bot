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

# --- CONFIGURAÇÕES DE IDS ---
# Agora usamos uma lista para os alvos (O usuário original + o Bot de Pokémon)
ALVOS_IDS = [716390085896962058, 854233015475109888]

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

# --- FUNÇÃO AUXILIAR: DOWNLOAD DE IMAGEM ---
async def download_image(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.read()
    except:
        return None

# --- FUNÇÃO DE ALERTA ---
async def enviar_alerta(message):
    # Criamos um embed decorativo personalizado
    embed_decoracao = discord.Embed(
        title="🐾 Captura de Dados Detectada!",
        description=f"**Origem:** {message.channel.mention}\n**Enviado por:** {message.author.mention}",
        color=0x7289da, # Blurple do Discord
        timestamp=datetime.now()
    )
    embed_decoracao.set_footer(text="Sistema de Monitoramento Ativo")

    # Coleta conteúdo e embeds originais
    conteudo_texto = message.content if message.content else ""
    embeds_para_enviar = [embed_decoracao]
    bytes_arquivos = []

    # Se a mensagem tiver Embeds (comum em bots de Pokémon)
    if message.embeds:
        for index, emb in enumerate(message.embeds):
            embeds_para_enviar.append(emb.copy()) # Copia o embed original
            
            # Tenta extrair imagem do embed (foto do pokémon)
            url_img = None
            if emb.image.url: url_img = emb.image.url
            elif emb.thumbnail.url: url_img = emb.thumbnail.url
            
            if url_img:
                img_data = await download_image(url_img)
                if img_data:
                    bytes_arquivos.append((img_data, f"pokemon_{index}.png"))

    # Processa anexos normais (se houver)
    if message.attachments:
        for att in message.attachments:
            att_data = await att.read()
            bytes_arquivos.append((att_data, att.filename))

    # Função interna para não "gastar" o BytesIO no primeiro envio
    def preparar_files():
        return [discord.File(io.BytesIO(b), filename=n) for b, n in bytes_arquivos]

    # --- ENVIO PARA VOCÊ ---
    try:
        await dm_cache[VOCE_ID].send(
            content=f"🔗 **Link:** {message.jump_url}\n{conteudo_texto}",
            embeds=embeds_para_enviar,
            files=preparar_files()
        )
    except Exception as e:
        print(f"Erro ao enviar DM para Você: {e}")

    # --- ENVIO PARA AMIGA ---
    try:
        nota = "💖 **Yori:** Veja isso, tsu! Um novo pokémon ou mensagem importante."
        await dm_cache[AMIGA_ID].send(
            content=f"{nota}\n🔗 {message.jump_url}\n{conteudo_texto}",
            embeds=embeds_para_enviar,
            files=preparar_files()
        )
    except Exception as e:
        print(f"Erro ao enviar DM para Amiga: {e}")

# --- EVENTOS ---

@bot.event
async def on_ready():
    print(f"🚀 Bot iniciado como {bot.user}")
    # Cache das DMs
    for uid in [AMIGA_ID, VOCE_ID]:
        try:
            user = await bot.fetch_user(uid)
            dm_cache[uid] = await user.create_dm()
        except:
            print(f"⚠️ Não foi possível abrir DM com {uid}")
    check_recent.start()

@bot.event
async def on_message(message):
    # Verifica se o autor é um dos alvos e se o canal está na lista
    if message.author.id in ALVOS_IDS and message.channel.id in CANAIS_MONITORADOS:
        if message.id not in mensagens_vistas:
            mensagens_vistas.add(message.id)
            await enviar_alerta(message)
    
    await bot.process_commands(message)

# --- LOOP DE VARREDURA (PARA CASO O BOT CAIA POR SEGUNDOS) ---
@tasks.loop(seconds=15)
async def check_recent():
    for guild in bot.guilds:
        for channel_id in CANAIS_MONITORADOS:
            channel = guild.get_channel(channel_id)
            if not channel: continue
            
            try:
                async for msg in channel.history(limit=15):
                    if (msg.author.id in ALVOS_IDS and 
                        msg.id not in mensagens_vistas and 
                        (datetime.now(timezone.utc) - msg.created_at).total_seconds() < 300):
                        
                        mensagens_vistas.add(msg.id)
                        await enviar_alerta(msg)
            except:
                continue

bot.run(TOKEN)
