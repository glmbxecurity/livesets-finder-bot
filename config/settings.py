import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables desde .env si existe
load_dotenv()

logger = logging.getLogger(__name__)

# Configuración del nivel de logs
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=log_level
)

# Palabras clave para validar si una entrada es un set musical
SET_KEYWORDS = [
    "set", "live", "session", "mix", "festival", 
    "podcast", "b2b", "dj set", "boiler room", "essential mix"
]


def get_bot_token() -> str:
    """Obtiene el token de Telegram desde las variables de entorno."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN no está definido en las variables de entorno o archivo .env")
        raise ValueError("Error crítico: La variable TELEGRAM_BOT_TOKEN es requerida.")
    return token


def get_artists_config() -> dict:
    """Carga y valida el archivo de artistas JSON."""
    file_path = os.getenv("ARTISTS_FILE", "artists.json")
    path = Path(file_path)

    if not path.exists():
        # Fallback para desarrollo si no existe artists.json pero sí artists.json.example
        example_path = Path("artists.json.example")
        if example_path.exists():
            logger.warning(f"'{file_path}' no encontrado. Usando '{example_path}' como fallback.")
            path = example_path
        else:
            logger.error(f"No se encontró el archivo de configuración de artistas en: {file_path}")
            return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.error(f"Estructura inválida en {path}: se esperaba un diccionario de géneros.")
                return {}
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error parseando JSON en {path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error inesperado leyendo {path}: {e}")
        return {}


def get_events_config() -> dict:
    """Carga y valida el archivo de eventos (festivales y clubes) JSON."""
    file_path = os.getenv("EVENTS_FILE", "events.json")
    path = Path(file_path)

    if not path.exists():
        example_path = Path("events.json.example")
        if example_path.exists():
            logger.warning(f"'{file_path}' no encontrado. Usando '{example_path}' como fallback.")
            path = example_path
        else:
            logger.error(f"No se encontró el archivo de configuración de eventos en: {file_path}")
            return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.error(f"Estructura inválida en {path}: se esperaba un diccionario de eventos.")
                return {}
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error parseando JSON en {path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error inesperado leyendo {path}: {e}")
        return {}

