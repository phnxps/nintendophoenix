PALABRAS_CLAVE_FUERTES = [
    "nintendo", "switch", "zelda", "mario", "pokemon", "joy-con", "kirby", "samus",
    "animal crossing", "metroid", "mario kart", "nintendo direct", "amiibo"
]

PALABRAS_PROHIBIDAS = [
    "doom", "fortnite", "playstation", "xbox", "baldur", "bungie", "steam", "valve",
    "anime", "pc", "ps5", "ps4", "game pass", "epic games", "elden ring"
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
