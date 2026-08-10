import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config.settings import get_artists_config, get_events_config, get_channels_config
from services.scraper import fetch_recent_sets_async

logger = logging.getLogger(__name__)


def clean_markdown_title(title: str) -> str:
    """Escapa adecuadamente caracteres conflictivos para Markdown de Telegram."""
    if not title:
        return ""
    for char in ['[', ']', '*', '_', '`']:
        title = title.replace(char, f'\\{char}')
    return title


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start: Muestra el menú principal con Géneros, Festivales, Canales y Set Aleatorio."""
    keyboard = [
        [InlineKeyboardButton("🎵 Buscar por Género (Artistas)", callback_data="mode:genres")],
        [InlineKeyboardButton("🎪 Buscar por Festival", callback_data="mode:events")],
        [InlineKeyboardButton("📺 Canales de YouTube", callback_data="mode:channels")],
        [InlineKeyboardButton("🎲 Set Aleatorio (Sorpresa)", callback_data="mode:random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🎧 *Bienvenido a LiveSets Finder Bot*\n\n"
        "¿Qué querés buscar hoy? Seleccioná una opción:"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def clean_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Elimina el mensaje actual de resultados y despliega un nuevo Menú Principal impecable."""
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"No se pudo eliminar el mensaje: {e}")

    keyboard = [
        [InlineKeyboardButton("🎵 Buscar por Género (Artistas)", callback_data="mode:genres")],
        [InlineKeyboardButton("🎪 Buscar por Festival", callback_data="mode:events")],
        [InlineKeyboardButton("📺 Canales de YouTube", callback_data="mode:channels")],
        [InlineKeyboardButton("🎲 Set Aleatorio (Sorpresa)", callback_data="mode:random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🎧 *Bienvenido a LiveSets Finder Bot*\n\n"
        "¿Qué querés buscar hoy? Seleccioná una opción:"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_genres_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de géneros musicales."""
    query = update.callback_query
    await query.answer()

    artists_config = get_artists_config()
    if not artists_config:
        await query.edit_message_text("❌ No se encontró la configuración de artistas (`artists.json`).")
        return

    genres = list(artists_config.keys())
    keyboard = []
    row = []
    for genre in genres:
        row.append(InlineKeyboardButton(genre, callback_data=f"select_genre:{genre}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("« Volver al Menú Principal", callback_data="back:main")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🎵 *Selecciona un género musical:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra opciones de festivales: Buscar en todos o seleccionar uno específico."""
    query = update.callback_query
    await query.answer()

    events_config = get_events_config()
    if not events_config:
        await query.edit_message_text("❌ No se encontró la configuración de eventos (`events.json`).")
        return

    keyboard = [
        [InlineKeyboardButton("🔥 Sets Más Recientes (Último Mes)", callback_data="event_mode:all")],
        [InlineKeyboardButton("🎯 Seleccionar Festival Específico (Último Año)", callback_data="event_mode:specific")],
        [InlineKeyboardButton("« Volver al Menú Principal", callback_data="back:main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🎪 *Búsqueda por Festival:*\n\n"
        "¿Cómo deseas buscar?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def specific_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la grilla con todos los festivales disponibles."""
    query = update.callback_query
    await query.answer()

    events_config = get_events_config()
    all_events = []
    for event_list in events_config.values():
        for ev in event_list:
            if ev.get("name"):
                all_events.append(ev.get("name"))

    keyboard = []
    row = []
    for name in all_events:
        row.append(InlineKeyboardButton(name, callback_data=f"select_event:{name}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("« Volver a Festivales", callback_data="mode:events")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🎪 *Selecciona un Festival:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra opciones para canales de YouTube: Buscar en todos o elegir uno específico."""
    query = update.callback_query
    await query.answer()

    channels_config = get_channels_config()
    if not channels_config:
        await query.edit_message_text("❌ No se encontró la configuración de canales (`channels.json`).")
        return

    keyboard = [
        [InlineKeyboardButton("🔥 Sets Más Recientes (Último Mes)", callback_data="channel_mode:all")],
        [InlineKeyboardButton("🎯 Seleccionar Canal Específico (Último Año)", callback_data="channel_mode:specific")],
        [InlineKeyboardButton("« Volver al Menú Principal", callback_data="back:main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📺 *Canales Oficiales de YouTube:*\n\n"
        "¿Cómo deseas buscar?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def specific_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra la grilla con los canales de YouTube configurados."""
    query = update.callback_query
    await query.answer()

    channels_config = get_channels_config()
    all_channels = []
    for ch_list in channels_config.values():
        for ch in ch_list:
            if ch.get("name"):
                all_channels.append(ch.get("name"))

    keyboard = []
    row = []
    for name in all_channels:
        row.append(InlineKeyboardButton(name, callback_data=f"select_channel:{name}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("« Volver a Canales", callback_data="mode:channels")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📺 *Selecciona un Canal de YouTube:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def select_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección para géneros, festivales o canales."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("select_genre:"):
        genre_name = data.split(":", 1)[1]
        context.user_data['search_type'] = "genre"
        context.user_data['selected_item'] = genre_name

        keyboard = [
            [
                InlineKeyboardButton("1 Mes", callback_data="months:1"),
                InlineKeyboardButton("3 Meses", callback_data="months:3"),
            ],
            [
                InlineKeyboardButton("6 Meses", callback_data="months:6"),
                InlineKeyboardButton("12 Meses", callback_data="months:12"),
            ],
            [
                InlineKeyboardButton("« Volver", callback_data="mode:genres")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"✅ Género seleccionado: *{genre_name}*\n\n"
            "📅 Selecciona el rango de antigüedad de los sets:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data.startswith("select_event:"):
        event_name = data.split(":", 1)[1]
        context.user_data['search_type'] = "event"
        context.user_data['selected_item'] = event_name
        await execute_search(update, context, months=12)
    elif data.startswith("select_channel:"):
        channel_name = data.split(":", 1)[1]
        context.user_data['search_type'] = "channel"
        context.user_data['selected_item'] = channel_name
        await execute_search(update, context, months=12)


async def all_events_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la búsqueda en todos los festivales fijado al último mes."""
    query = update.callback_query
    await query.answer()

    context.user_data['search_type'] = "all_events"
    context.user_data['selected_item'] = "Todos los Festivales"
    await execute_search(update, context, months=1)


async def all_channels_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la búsqueda en todos los canales de YouTube fijado al último mes."""
    query = update.callback_query
    await query.answer()

    context.user_data['search_type'] = "all_channels"
    context.user_data['selected_item'] = "Todos los Canales"
    await execute_search(update, context, months=1)


async def random_set_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene y presenta un set musical aleatorio de la base de artistas, festivales o canales."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("🎲 *Sorteando y buscando un set aleatorio...*", parse_mode="Markdown")

    artists_config = get_artists_config()
    events_config = get_events_config()
    channels_config = get_channels_config()

    candidates = []

    for genre, artist_list in artists_config.items():
        for art in artist_list:
            candidates.append({
                "name": art.get("name"),
                "sources": art.get("sources", []),
                "type": f"Artista ({genre})"
            })

    for cat, event_list in events_config.items():
        for ev in event_list:
            candidates.append({
                "name": ev.get("name"),
                "sources": ev.get("sources", []),
                "type": "Festival"
            })

    for cat, channel_list in channels_config.items():
        for ch in channel_list:
            candidates.append({
                "name": ch.get("name"),
                "sources": ch.get("sources", []),
                "type": "Canal YouTube"
            })

    if not candidates:
        await query.edit_message_text("❌ No hay artistas, festivales ni canales configurados en el bot.")
        return

    attempts = 0
    found_set = None
    chosen_candidate = None

    while attempts < 3 and not found_set:
        attempts += 1
        candidate = random.choice(candidates)
        sets = await fetch_recent_sets_async(candidate["name"], candidate["sources"], 12)
        if sets:
            found_set = random.choice(sets)
            chosen_candidate = candidate

    keyboard = [
        [InlineKeyboardButton("🎲 Buscar Otro Set Aleatorio", callback_data="mode:random")],
        [
            InlineKeyboardButton("🏠 Menú Principal", callback_data="back:main"),
            InlineKeyboardButton("🗑️ Limpiar e Inicio", callback_data="clean:start")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if not found_set:
        await query.edit_message_text(
            "🚫 No se encontró ningún set aleatorio en este intento. ¡Prueba otra vez!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    title_clean = clean_markdown_title(found_set['title'])
    dur_info = f" (`{found_set['duration_min']} min`)" if found_set.get('duration_min') else ""

    msg_text = (
        "🎲 *Set Aleatorio Sorpresa Found!*\n\n"
        f"📍 *{clean_markdown_title(chosen_candidate['name'])}* _{clean_markdown_title(chosen_candidate['type'])}_\n"
        f"🎧 [{title_clean}]({found_set['url']}){dur_info}\n\n"
        f"🗓️ Fecha/Estado: `{found_set.get('upload_date', 'Desconocida')}`"
    )

    await query.edit_message_text(
        msg_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


async def execute_search(update: Update, context: ContextTypes.DEFAULT_TYPE, months: int):
    """Ejecuta la búsqueda según el tipo seleccionado y envía los resultados."""
    query = update.callback_query
    search_type = context.user_data.get('search_type', 'genre')
    selected_item = context.user_data.get('selected_item')

    if not selected_item:
        msg = "⚠️ Selección vencida o inválida. Usá /start para comenzar."
        if query:
            await query.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return

    label = f"sets de *{clean_markdown_title(selected_item)}*" if search_type in ("event", "all_events", "channel", "all_channels") else f"sets del género *{clean_markdown_title(selected_item)}*"
    status_text = f"🔍 Buscando {label} (últimos *{months}* meses)...\nEsto puede demorar unos segundos."
    
    if query:
        await query.edit_message_text(status_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(status_text, parse_mode="Markdown")

    results_blocks = []
    found_total = 0

    if search_type == "genre":
        artists_config = get_artists_config()
        artists = artists_config.get(selected_item, [])
        tasks = [fetch_recent_sets_async(a.get('name', 'Artista'), a.get('sources', []), months) for a in artists]
        all_sets_results = await asyncio.gather(*tasks)

        for artist, sets in zip(artists, all_sets_results):
            if sets:
                name = artist.get('name', 'Artista')
                found_total += len(sets)
                block = [f"👤 *{clean_markdown_title(name)}*"]
                for item in sets[:5]:
                    title_clean = clean_markdown_title(item['title'])
                    dur_info = f" (`{item['duration_min']} min`)" if item.get('duration_min') else ""
                    block.append(f"• [{title_clean}]({item['url']}){dur_info}")
                results_blocks.append("\n".join(block))

    elif search_type == "event":
        events_config = get_events_config()
        event_sources = []
        for cat_list in events_config.values():
            for ev in cat_list:
                if ev.get("name") == selected_item:
                    event_sources = ev.get("sources", [])
                    break

        sets = await fetch_recent_sets_async(selected_item, event_sources, months)
        if sets:
            found_total += len(sets)
            block = [f"🎪 *{clean_markdown_title(selected_item)}*"]
            for item in sets[:8]:
                title_clean = clean_markdown_title(item['title'])
                dur_info = f" (`{item['duration_min']} min`)" if item.get('duration_min') else ""
                block.append(f"• [{title_clean}]({item['url']}){dur_info}")
            results_blocks.append("\n".join(block))

    elif search_type == "all_events":
        events_config = get_events_config()
        all_festivals = []
        for cat_list in events_config.values():
            for ev in cat_list:
                if ev.get("name"):
                    all_festivals.append(ev)

        tasks = [fetch_recent_sets_async(ev.get("name"), ev.get("sources", []), months) for ev in all_festivals]
        all_sets_results = await asyncio.gather(*tasks)

        for ev, sets in zip(all_festivals, all_sets_results):
            if sets:
                ev_name = ev.get("name")
                found_total += len(sets)
                block = [f"🎪 *{clean_markdown_title(ev_name)}*"]
                for item in sets[:3]:
                    title_clean = clean_markdown_title(item['title'])
                    dur_info = f" (`{item['duration_min']} min`)" if item.get('duration_min') else ""
                    block.append(f"• [{title_clean}]({item['url']}){dur_info}")
                results_blocks.append("\n".join(block))

    elif search_type == "channel":
        channels_config = get_channels_config()
        ch_sources = []
        for cat_list in channels_config.values():
            for ch in cat_list:
                if ch.get("name") == selected_item:
                    ch_sources = ch.get("sources", [])
                    break

        sets = await fetch_recent_sets_async(selected_item, ch_sources, months)
        if sets:
            found_total += len(sets)
            block = [f"📺 *{clean_markdown_title(selected_item)}*"]
            for item in sets[:8]:
                title_clean = clean_markdown_title(item['title'])
                dur_info = f" (`{item['duration_min']} min`)" if item.get('duration_min') else ""
                block.append(f"• [{title_clean}]({item['url']}){dur_info}")
            results_blocks.append("\n".join(block))

    elif search_type == "all_channels":
        channels_config = get_channels_config()
        all_channels = []
        for cat_list in channels_config.values():
            for ch in cat_list:
                if ch.get("name"):
                    all_channels.append(ch)

        tasks = [fetch_recent_sets_async(ch.get("name"), ch.get("sources", []), months) for ch in all_channels]
        all_sets_results = await asyncio.gather(*tasks)

        for ch, sets in zip(all_channels, all_sets_results):
            if sets:
                ch_name = ch.get("name")
                found_total += len(sets)
                block = [f"📺 *{clean_markdown_title(ch_name)}*"]
                for item in sets[:3]:
                    title_clean = clean_markdown_title(item['title'])
                    dur_info = f" (`{item['duration_min']} min`)" if item.get('duration_min') else ""
                    block.append(f"• [{title_clean}]({item['url']}){dur_info}")
                results_blocks.append("\n".join(block))

    nav_keyboard = [
        [
            InlineKeyboardButton("🏠 Menú Principal", callback_data="back:main"),
            InlineKeyboardButton("🗑️ Limpiar e Inicio", callback_data="clean:start")
        ]
    ]
    nav_markup = InlineKeyboardMarkup(nav_keyboard)

    if found_total == 0:
        final_msg = f"🚫 No se encontraron {label} en los últimos *{months}* meses."
        if query:
            await query.edit_message_text(final_msg, reply_markup=nav_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(final_msg, reply_markup=nav_markup, parse_mode="Markdown")
        return

    header = f"🎧 *LiveSets encontrados: {clean_markdown_title(selected_item)}* (últimos {months} meses)\n\n"
    full_message = header + "\n\n".join(results_blocks)

    chunk_size = 3800
    if len(full_message) <= chunk_size:
        if query:
            await query.edit_message_text(full_message, reply_markup=nav_markup, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text(full_message, reply_markup=nav_markup, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        chunks = []
        curr_chunk = header
        for block in results_blocks:
            if len(curr_chunk) + len(block) + 2 > chunk_size:
                chunks.append(curr_chunk)
                curr_chunk = block
            else:
                curr_chunk += ("\n\n" if curr_chunk != header else "") + block
        if curr_chunk:
            chunks.append(curr_chunk)

        if query:
            await query.edit_message_text(chunks[0], parse_mode="Markdown", disable_web_page_preview=True)
            for ch in chunks[1:-1]:
                await query.message.reply_text(ch, parse_mode="Markdown", disable_web_page_preview=True)
            await query.message.reply_text(chunks[-1], reply_markup=nav_markup, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            for ch in chunks[:-1]:
                await update.message.reply_text(ch, parse_mode="Markdown", disable_web_page_preview=True)
            await update.message.reply_text(chunks[-1], reply_markup=nav_markup, parse_mode="Markdown", disable_web_page_preview=True)


async def months_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el callback del botón de antigüedad en meses."""
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("months:"):
        return

    months = int(query.data.split(":", 1)[1])
    await execute_search(update, context, months)


async def months_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback si el usuario escribe el número manualmente."""
    text = update.message.text.strip()
    try:
        months = int(text)
        if months <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_text(
            "❌ *Entrada no válida.* Por favor seleccioná una opción de los botones o enviá un número entero mayor a 0.",
            parse_mode="Markdown"
        )
        return

    await execute_search(update, context, months)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Manejador global de excepciones en el bot."""
    logger.error("Excepción al procesar actualización:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Ocurrió un error interno al procesar tu solicitud. Por favor intenta más tarde."
        )


def setup_handlers(app: Application):
    """Registra todos los handlers en la aplicación de Telegram."""
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(start_command, pattern="^back:main$"))
    app.add_handler(CallbackQueryHandler(clean_start_callback, pattern="^clean:start$"))
    app.add_handler(CallbackQueryHandler(show_genres_menu, pattern="^mode:genres$"))
    app.add_handler(CallbackQueryHandler(show_events_menu, pattern="^mode:events$"))
    app.add_handler(CallbackQueryHandler(show_channels_menu, pattern="^mode:channels$"))
    app.add_handler(CallbackQueryHandler(specific_events_menu, pattern="^event_mode:specific$"))
    app.add_handler(CallbackQueryHandler(all_events_callback, pattern="^event_mode:all$"))
    app.add_handler(CallbackQueryHandler(specific_channels_menu, pattern="^channel_mode:specific$"))
    app.add_handler(CallbackQueryHandler(all_channels_callback, pattern="^channel_mode:all$"))
    app.add_handler(CallbackQueryHandler(random_set_callback, pattern="^mode:random$"))
    app.add_handler(CallbackQueryHandler(select_item_callback, pattern="^select_(genre|event|channel):"))
    app.add_handler(CallbackQueryHandler(months_callback, pattern="^months:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, months_input_handler))
    app.add_error_handler(error_handler)
