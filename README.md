<p align="center">
  <img src="livesetsfinder.png" alt="LiveSets Finder Bot Logo" width="300" />
</p>

# 🎧 LiveSets Finder Bot

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/telegram--bot--api-v20%2B-paperplane.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20Mint%20%7C%20Ubuntu%20%7C%20Alpine%20LXC-success.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**LiveSets Finder Bot** es un bot de Telegram stateless y de alto rendimiento construido en Python. Permite rastrear, filtrar y listar de forma asíncrona y paralela sets musicales, sesiones en vivo y podcasts desde **YouTube** y **SoundCloud**.

Permite explorar por **Géneros / Artistas**, **Festivales**, **Canales Oficiales de YouTube**, o descubrir un **Set Aleatorio**, filtrando el contenido reciente con una regla estricta de duración mínima (≥ 40 minutos) para excluir canciones sueltas o previews.

---

## 📖 ¿En qué consiste este proyecto?

El bot lee dinámicamente los artistas desde `artists.json` (4 géneros y 50 artistas), los eventos desde `events.json` (26 festivales icónicos) y los canales oficiales desde `channels.json` (14 canales principales). Ejecuta consultas concurrentes en segundo plano usando un pool de hilos (`ThreadPoolExecutor` + `asyncio.gather`), reduciendo los tiempos de escaneo masivo a solo ~35 segundos.

### 🌟 Características Destacadas:
* **4 Modos de Búsqueda Integrados**: 
  * 🎵 **Por Género (Artistas)**: Selección por género (Techno, Melodic Techno, Hard Techno, Hard Dance), filtros de antigüedad (`1`, `3`, `6`, `12` meses) y botón de **`🎲 Set Aleatorio (Género)`**.
  * 🎪 **Por Festival**:
    * 🔥 *Sets Más Recientes (Último Mes)*: Escaneo paralelo de los 26 festivales en los últimos 30 días.
    * 🎯 *Festival Específico (Último Año)*: Búsqueda directa en los últimos 12 meses.
    * 🎲 *Set Aleatorio de Festival*: Sorteo exclusivo dentro de los 26 festivales.
  * 📺 **Canales Oficiales de YouTube**:
    * 🔥 *Sets Más Recientes (Último Mes)*: Escaneo paralelo de los 14 canales oficiales.
    * 🎯 *Canal Específico (Último Año)*: Búsqueda directa en el canal seleccionado.
    * 🎲 *Set Aleatorio de Canal*: Sorteo exclusivo dentro de los canales oficiales.
  * 🎲 **Set Aleatorio Global (Sorpresa)**: Sorteo sorpresa entre todos los artistas, festivales y canales configurados.
* **Procesamiento Concurrente de Alto Rendimiento**: Peticiones a YouTube y SoundCloud optimizadas mediante hilos concurrentes para evitar bloqueos del event loop y reducir latencias.
* **Filtrado Inteligente (≥ 40 min)**: Validación estricta por palabras clave en vivo y duración mínima de 40 minutos para descartar singles, remixes o canciones.
* **Navegación Limpia & Auto-Eliminación**:
  * **`🏠 Menú Principal`**: Retorna al menú de inicio.
  * **`🗑️ Limpiar e Inicio`**: Elimina automáticamente el mensaje de resultados anterior y envía una pantalla limpia.
* **Escapado Seguro de Markdown**: Sanitizado automático de títulos (`clean_markdown_title`) para evitar fallos de parseo en Telegram.
* **Sin Reinicios (Live Reload)**: Los archivos `artists.json`, `events.json` y `channels.json` se leen en tiempo real en cada consulta.
* **Multi-Despliegue**: Soporte para **Systemd (Linux Mint / Ubuntu / Debian)** y **OpenRC (Alpine Linux LXC)**.

---

## 🤖 Paso 1: Crear el Bot en Telegram

1. Abrí Telegram y buscá [@BotFather](https://t.me/BotFather).
2. Iniciá el chat y enviá el comando `/newbot`.
3. Asignale un nombre y username a tu bot.
4. Guardá el token de API (ej: `7123456789:ABCdefGHIjklMNOpqrsTUVwxyZ`).

---

## 🛠️ Paso 2: Instalación de Requisitos del Sistema

### En Linux Mint / Ubuntu / Debian (`apt`)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg git -y
```

### En Alpine Linux LXC (`apk`)
```bash
apk update
apk add python3 py3-pip ffmpeg git
```

---

## ⚙️ Paso 3: Configuración del Proyecto

1. Cloná el repositorio e ingresá al directorio:
   ```bash
   git clone https://github.com/tu-usuario/livesets-finder-bot.git
   cd livesets-finder-bot
   ```

2. Creá el entorno virtual e instalá las dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno (`.env`):
   ```bash
   cp .env.example .env
   ```
   Edita `.env` con tu token:
   ```env
   TELEGRAM_BOT_TOKEN=7123456789:ABCdefGHIjklMNOpqrsTUVwxyZ
   ARTISTS_FILE=artists.json
   EVENTS_FILE=events.json
   CHANNELS_FILE=channels.json
   LOG_LEVEL=INFO
   ```

4. Configurar Artistas (`artists.json`), Festivales (`events.json`) y Canales (`channels.json`):
   ```bash
   cp artists.json.example artists.json
   cp events.json.example events.json
   cp channels.json.example channels.json
   ```

---

## 🚀 Paso 4: Ejecución Local

```bash
source venv/bin/activate
python main.py
```

---

## 📱 Paso 5: Interacción en Telegram

1. Enviá `/start` para desplegar el menú principal.
2. Navegá por los botones interactivos:
   * **🎵 Buscar por Género (Artistas)** → Elegí género, rango de meses o set aleatorio de ese género.
   * **🎪 Buscar por Festival** → Elegí *Último Mes*, *Festival Específico* o *Set Aleatorio de Festival*.
   * **📺 Canales de YouTube** → Elegí *Último Mes*, *Canal Específico* o *Set Aleatorio de Canal*.
   * **🎲 Set Aleatorio (Sorpresa)** → Obtené un set recomendado al azar de toda la base de datos.

---

## ⚙️ Paso 6: Servicio en Segundo Plano (Producción)

### Systemd (Linux Mint / Ubuntu / Debian)
```bash
sudo cp deploy/livesets-finder-bot.service /etc/systemd/system/livesets-finder-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now livesets-finder-bot
```

### OpenRC (Alpine Linux LXC en Proxmox)
```bash
cp deploy/livesets-finder-bot.initd /etc/init.d/livesets-finder-bot
chmod +x /etc/init.d/livesets-finder-bot
rc-service livesets-finder-bot start
rc-update add livesets-finder-bot default
```

#### 💡 Solución de Problemas (Troubleshooting OpenRC)
Si el bot indica `Conflict: terminated by other getUpdates request` o el servicio queda en estado `crashed`/`unsupervised`:
```bash
rc-service livesets-finder-bot zap
rc-service livesets-finder-bot start
```

---

## 📂 Estructura del Repositorio

```
livesets-finder-bot/
├── bot/
│   ├── __init__.py
│   └── handlers.py          # Handlers de menú principal, aleatorio, géneros, festivales y canales
├── config/
│   ├── __init__.py
│   └── settings.py          # Carga de .env, logger y parseo en vivo de JSONs
├── services/
│   ├── __init__.py
│   └── scraper.py           # Extracción concurrente con yt-dlp (ThreadPoolExecutor)
├── deploy/
│   ├── livesets-finder-bot.service # Servicio Systemd (Linux Mint/Ubuntu)
│   └── livesets-finder-bot.initd   # Servicio OpenRC (Alpine LXC)
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Exclusiones de Git
├── artists.json              # 44 Artistas activos organizados por 4 géneros
├── artists.json.example      # Plantilla y respaldo completo de artistas
├── events.json               # 26 Festivales activos
├── events.json.example       # Plantilla y respaldo completo de eventos
├── channels.json             # 11 Canales oficiales de YouTube
├── channels.json.example     # Plantilla y respaldo completo de canales
├── livesetsfinder.png        # Logo oficial del bot
├── main.py                   # Entrypoint del bot de Telegram
├── requirements.txt          # Dependencias de Python fijadas
└── README.md                 # Documentación completa
```