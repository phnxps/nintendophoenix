# Encabezado del archivo
import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

saved_articles = set()

RSS_FEEDS = [
    'https://vandal.elespanol.com/rss/',
    'https://www.3djuegos.com/rss/',
    'https://www.hobbyconsolas.com/categoria/novedades/rss',
    'https://www.vidaextra.com/feed',
    'https://es.ign.com/rss',
    'https://www.nintenderos.com/feed',
    'https://as.com/meristation/portada/rss.xml',
    'https://blog.es.playstation.com/feed/',
    'https://www.nintendo.com/es/news/rss.xml',
    'https://news.xbox.com/es-mx/feed/',
    'https://nintenduo.com/category/noticias/feed/',
    'https://www.xataka.com/tag/nintendo/rss',
    'https://www.eurogamer.es/rss',
    'https://www.xataka.com/tag/playstation/rss',
    'https://www.laps4.com/feed/',
    'https://www.gamereactor.es/rss/rss.php?texttype=1',
    'https://areajugones.sport.es/feed/',
]

PALABRAS_CLAVE_NINTENDO = [
    "nintendo", "switch", "switch 2", "nintendo switch", "zelda", "link", "mario",
    "super mario", "luigi", "peach", "yoshi", "bowser", "donkey kong", "metroid",
    "samus", "kirby", "smash", "smash bros", "joy-con", "pokemon", "pikachu",
    "game freak", "animal crossing", "new horizons", "splatoon", "bayonetta",
    "mii", "amiibo", "mario kart", "hyrule", "nintendogs", "ds", "3ds", "wii", "wii u",
    "eshop", "super smash bros", "nintendo direct", "pokemon presents",
    "paper mario", "nintendo labo", "switch oled", "switch lite"
]

PALABRAS_CLAVE_FUERTES = [
    "nintendo", "switch", "zelda", "mario", "pokemon", "joy-con", "kirby", "samus",
    "animal crossing", "metroid", "mario kart", "nintendo direct", "amiibo"
]

PALABRAS_PROHIBIDAS = [
    "playstation", "xbox", "baldur", "bungie", "steam", "valve",
    "anime", "pc", "ps5", "ps4", "game pass"
]

async def send_news(context, entry):
    if hasattr(entry, 'published_parsed'):
        published = datetime(*entry.published_parsed[:6])
        if datetime.now() - published > timedelta(hours=3):
            return

    title_lower = entry.title.lower()
    summary_lower = (entry.summary if hasattr(entry, 'summary') else "").lower()

    if not any(p in title_lower or p in summary_lower for p in PALABRAS_CLAVE_NINTENDO):
        return
    if not any(p in title_lower or p in summary_lower for p in PALABRAS_CLAVE_FUERTES):
        return
    if any(w in title_lower for w in PALABRAS_PROHIBIDAS):
        return
    if "nintendo" not in entry.link.lower() and not any(p in title_lower + summary_lower for p in PALABRAS_CLAVE_FUERTES):
        return

    if entry.link in saved_articles:
        return

    link = entry.link
    photo_url = None

    if entry.get("media_content"):
        for m in entry.media_content:
            if m.get("type", "").startswith("image/"):
                photo_url = m.get("url")
                break
    if not photo_url and entry.get("enclosures"):
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                photo_url = enc.get("url")
                break
    if not photo_url:
        try:
            r = requests.get(entry.link, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                photo_url = og_image.get('content')
        except Exception as e:
            print(f"Error obteniendo imagen: {e}")

    # 💡 Clasificación dinámica del tipo de noticia
    if any(k in title_lower for k in ["direct", "evento", "presentación", "showcase"]):
        tipo = "🎬 *EVENTO NINTENDO*"
    elif any(k in title_lower for k in ["tráiler", "trailer", "avance", "gameplay"]):
        tipo = "🎥 *TRÁILER DE NINTENDO*"
    elif any(k in title_lower for k in ["review", "análisis", "reseña", "comparativa"]):
        tipo = "📝 *REVIEW NINTENDO*"
    elif any(k in title_lower for k in ["rebaja", "oferta", "descuento", "promoción"]):
        tipo = "💸 *OFERTA NINTENDO*"
    elif any(k in title_lower for k in ["lanzamiento", "llega", "disponible", "estrena"]):
        tipo = "🎮 *LANZAMIENTO NINTENDO*"
    else:
        tipo = "🍄 *NOTICIA NINTENDO*"

    caption = f"{tipo}\n\n*{entry.title}*\n\n#Nintendo"
    button = InlineKeyboardMarkup([[InlineKeyboardButton("📰 Leer noticia completa", url=entry.link)]])

    try:
        if photo_url:
            await context.bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=photo_url,
                caption=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                reply_markup=button
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                disable_web_page_preview=False,
                reply_markup=button
            )
        saved_articles.add(entry.link)
    except Exception as e:
        print(f"Error al enviar noticia: {e}")

async def check_feeds(context):
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            await send_news(context, entry)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.job_queue.run_repeating(check_feeds, interval=600, first=10)
    print("Bot Nintendo listo y filtrando noticias correctamente.")
    application.run_polling()

if __name__ == "__main__":
    main()
