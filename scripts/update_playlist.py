import urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
OUTPUT = Path("IPTV_Grado_Full_v1.0.m3u")

# Stream incompatibili con SS IPTV sulla nostra Hisense/VIDAA.
BLOCKED = (
    "live02-seg.msf.cdn.mediaset.net",
)

# Canali che vogliamo nella nostra IPTV Grado.
WANTED = [
    "Rai 1", "Rai 2", "Rai 3", "La7", "TV8", "Nove",
    "Rai 4", "Rai 5", "Rai Movie", "Rai Premium",
    "Cielo", "TV 2000", "Real Time", "Food Network",
    "Discovery Channel", "Giallo", "DMAX", "HGTV",
    "Alma TV", "Gambero Rosso", "MAN-GA", "Turbo", "Travel TV",
    "K2", "Rai Gulp", "Rai YoYo", "Frisbee", "Super!", "BeJoy.Kids",
    "Rai News 24", "Sky TG24", "Rai Storia", "Rai Scuola",
    "Senato TV", "Camera dei Deputati", "Euronews Italian",
    "Rai Sport", "Sportitalia Plus", "SuperTennis",
    "Sportitalia SOLOCALCIO", "BIKE Channel",
    "Radio TV Serie A con RDS", "RTL 102.5", "Radio 105 TV",
    "R101 TV", "Deejay TV", "RadioItaliaTV", "Radio KISS KISS TV",
    "Rai Radio 2 Visual Radio", "Radio24-IlSole24OreTV",
    "RadioFreccia", "RDS Social TV", "Radio ZETA",
    "Radio Montecarlo TV", "Virgin Radio TV", "Radio m2o Tv",
    "Radio Norba Tv",
    "Tele Quattro Trieste", "Tele Friuli",
    "Tele Pordenone", "Ran Friul", "Videotelecarnia"
]


def clean_name(name):
    """Normalizza il nome del canale."""
    for symbol in "ⒼⓈⓎⓉ":
        name = name.replace(symbol, "")
    return " ".join(name.split()).strip().lower()


def download():
    """Scarica la playlist sorgente."""
    request = urllib.request.Request(
        SOURCE,
        headers={"User-Agent": "IPTV-Grado/2.1"}
    )

    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read().decode(
            "utf-8-sig",
            errors="replace"
        )


def parse(text):
    """
    Legge la playlist M3U e restituisce:
    nome, EXTINF, righe aggiuntive, URL.
    """
    lines = text.splitlines()
    channels = []

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if not line.startswith("#EXTINF"):
            i += 1
            continue

        info = line
        name = info.split(",", 1)[-1].strip()

        i += 1
        extras = []
        url = None

        while i < len(lines):

            current = lines[i].strip()

            if current.startswith("#EXTINF"):
                break

            if current.startswith(("http://", "https://")):
                url = current
                i += 1
                break

            if current:
                extras.append(current)

            i += 1

        if url:
            channels.append(
                (name, info, extras, url)
            )

    return channels


def stream_score(url):
    """
    Preferenza fra eventuali stream duplicati.

    Per Rai preferiamo CloudFront quando disponibile,
    perché è un normale HLS diretto.

    Gli altri stream ricevono un punteggio neutro.
    """

    score = 0

    lower = url.lower()

    if "cloudfront.net" in lower:
        score += 20

    if ".m3u8" in lower:
        score += 10

    if "relinker" in lower:
        score += 5

    return score


# ---------------------------------------------------------
# DOWNLOAD E ANALISI
# ---------------------------------------------------------

text = download()
source_channels = parse(text)

wanted = {
    clean_name(channel): channel
    for channel in WANTED
}

# Raggruppa gli stream disponibili per canale.
candidates = {}

for name, info, extras, url in source_channels:

    normalized = clean_name(name)

    if normalized not in wanted:
        continue

    # Esclude stream incompatibili.
    if any(domain in url for domain in BLOCKED):
        print("BLOCCATO:", name, url)
        continue

    candidates.setdefault(normalized, []).append(
        (name, info, extras, url)
    )


# ---------------------------------------------------------
# COSTRUZIONE PLAYLIST
# ---------------------------------------------------------

output = [
    "#EXTM3U",
    "#PLAYLIST:IPTV Grado - Safe Auto Update",
    "#NOTA:Aggiornamento automatico protetto per Hisense VIDAA / SS IPTV"
]

added = set()
count = 0

# Manteniamo l'ordine definito nella nostra lista WANTED.
for requested_name in WANTED:

    normalized = clean_name(requested_name)

    available = candidates.get(normalized, [])

    if not available:
        print("NON TROVATO:", requested_name)
        continue

    # Se esistono più URL dello stesso canale,
    # prende quello con il punteggio migliore.
    best = max(
        available,
        key=lambda channel: stream_score(channel[3])
    )

    name, info, extras, url = best

    # Ulteriore sicurezza contro duplicati.
    if normalized in added:
        continue

    added.add(normalized)

    # Telequattro deve apparire come canale 10.
    if normalized == clean_name("Tele Quattro Trieste"):
        info = info.rsplit(",", 1)[0] + ",10 - Telequattro"

    output.append(info)
    output.extend(extras)
    output.append(url)

    count += 1

    print("AGGIUNTO:", requested_name, url)


# ---------------------------------------------------------
# CONTROLLO DI SICUREZZA
# ---------------------------------------------------------

# Se la sorgente cambia drasticamente o si verifica
# un problema, NON distruggiamo la playlist precedente.
if count < 35:
    raise RuntimeError(
        f"Trovati soltanto {count} canali. "
        "Aggiornamento annullato e playlist precedente preservata."
    )


# ---------------------------------------------------------
# SALVATAGGIO
# ---------------------------------------------------------

OUTPUT.write_text(
    "\n".join(output) + "\n",
    encoding="utf-8"
)

print("--------------------------------------")
print(f"IPTV Grado aggiornata: {count} canali.")
print("Duplicati eliminati.")
print("Stream Mediaset incompatibili esclusi.")
print("--------------------------------------")
