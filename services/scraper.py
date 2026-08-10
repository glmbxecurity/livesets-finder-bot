import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import yt_dlp

logger = logging.getLogger(__name__)

# Palabras clave obligatorias para identificar un set
SET_KEYWORDS = [
    'set', 'live', 'session', 'mix', 'festival', 'podcast',
    'b2b', 'boiler room', 'essential mix', 'radio show', 'live at',
    'live @', 'live from'
]

# Palabras clave para excluir explícitamente canciones, sencillos y previews
EXCLUDE_KEYWORDS = [
    'original mix', 'extended mix', 'club mix', 'instrumental mix',
    'radio edit', 'official audio', 'official video', 'preview',
    'teaser', 'snippet', 'short', 'full track', 'remix', 'single',
    'official music video', 'lyric video'
]

# Duración mínima en segundos (40 minutos = 2400 segundos)
MIN_DURATION_SECONDS = 2400


def is_valid_set(title: str, duration: float | None) -> bool:
    """Valida si una entrada corresponde a un set musical continuo."""
    if not title:
        return False
        
    title_lower = title.lower()

    if any(ex in title_lower for ex in EXCLUDE_KEYWORDS):
        return False

    if duration is not None and duration < MIN_DURATION_SECONDS:
        return False

    return any(kw in title_lower for kw in SET_KEYWORDS)


def _process_single_query(query: str, cutoff_date: datetime) -> list[dict]:
    """Procesa una consulta individual de yt-dlp de forma segura en un hilo."""
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'playlistend': 15,
    }

    query_results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if not info:
                return []

            entries = info.get('entries', []) if 'entries' in info else [info]

            for entry in entries:
                if not entry:
                    continue

                title = entry.get('title', '')
                duration = entry.get('duration')

                if not is_valid_set(title, duration):
                    continue

                upload_date_str = entry.get('upload_date')
                timestamp = entry.get('timestamp')
                pub_date = None

                if upload_date_str:
                    try:
                        pub_date = datetime.strptime(upload_date_str, "%Y%m%d")
                    except ValueError:
                        pass
                elif timestamp:
                    try:
                        pub_date = datetime.fromtimestamp(timestamp)
                    except (ValueError, TypeError, OSError):
                        pass

                if pub_date and pub_date < cutoff_date:
                    continue

                url = entry.get('webpage_url') or entry.get('url')
                if url and not url.startswith("http"):
                    url = f"https://www.youtube.com/watch?v={url}"

                if url:
                    query_results.append({
                        'title': title,
                        'url': url,
                        'duration_min': round(duration / 60, 1) if duration else None,
                        'upload_date': pub_date.strftime('%Y-%m-%d') if pub_date else 'Desconocida'
                    })
    except Exception as e:
        logger.error(f"Error procesando query '{query}': {e}")

    return query_results


def _sync_fetch_recent_sets(artist_name: str, sources: list[str], months_limit: int) -> list[dict]:
    """Extracción concurrente con ThreadPoolExecutor para acelerar las peticiones HTTP."""
    cutoff_date = datetime.now() - timedelta(days=months_limit * 30)

    # Términos de búsqueda dinámica
    search_terms = ["live set", "live", "set", "full set"]
    search_queries = []
    for term in search_terms:
        search_queries.append(f"ytsearch3:{artist_name} {term}")
        search_queries.append(f"scsearch3:{artist_name} {term}")
    search_queries.extend(sources)

    results = []
    seen_urls = set()

    # Ejecutar hasta 6 hilos simultáneos para no saturar ni ser baneados por IP
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_process_single_query, q, cutoff_date) for q in search_queries]
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        results.append(item)
            except Exception as e:
                logger.error(f"Error extrayendo resultados para '{artist_name}': {e}")

    return results


async def fetch_recent_sets_async(artist_name: str, sources: list[str], months_limit: int) -> list[dict]:
    """Wrapper asíncrono para delegar la extracción concurrente en un hilo secundario."""
    return await asyncio.to_thread(_sync_fetch_recent_sets, artist_name, sources, months_limit)
