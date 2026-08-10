#!/usr/bin/env python3
"""
LiveSets Finder Bot - Entrypoint Principal

Bot de Telegram asíncrono para búsqueda de sets musicales en YouTube y SoundCloud
organizados por género y rango de antigüedad en meses.
"""

import logging
from telegram.ext import ApplicationBuilder
from config.settings import get_bot_token
from bot.handlers import setup_handlers

logger = logging.getLogger(__name__)


def main():
    """Inicializa y ejecuta el bot de Telegram."""
    logger.info("Iniciando LiveSets Finder Bot...")

    try:
        token = get_bot_token()
    except ValueError as e:
        logger.critical(f"Fallo al iniciar el bot: {e}")
        return

    app = ApplicationBuilder().token(token).build()

    # Registrar handlers modularizados
    setup_handlers(app)

    logger.info("Bot iniciado correctamente. Escuchando eventos (polling)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
