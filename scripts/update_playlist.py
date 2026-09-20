import urllib.request
from pathlib import Path

SOURCE = (
    "https://raw.githubusercontent.com/"
    "Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
)

OUTPUT = Path("IPTV_Grado_Full_v1.0.m3u")


# =========================================================
# IPTV GRADO - SAFE AUTO UPDATE
# Versione 2.2 - Hisense VIDAA / SS IPTV
# =========================================================


# Stream che sulla nostra Hisense / SS IPTV hanno dato
# problemi di congelamento.
BLOCKED = (
    "live02-seg.msf.cdn.mediaset.net",
)


# Canali che vogliamo mantenere nella playlist.
WANTED = [
    "Rai 1",
    "Rai 2",
    "Rai 3",
    "La7",
    "TV8",
    "Nove",

    "Rai 4",
    "Rai 5",
    "Rai Movie",
    "Rai Premium",

    "Cielo",
    "TV 2000",
    "Real Time",
    "Food Network",
    "Discovery Channel",
    "Giallo",
    "DMAX",
    "HGTV",

    "Alma TV",
    "Gambero Rosso",
    "MAN-GA",
    "Turbo",
    "Travel TV",

    "K2",
    "Rai Gulp",
    "Rai YoYo",
    "Frisbee",
    "Super!",
    "BeJoy.Kids",

    "Rai News 24",
    "Sky TG24",
    "Rai Storia",
    "Rai Scuola",

    "Senato TV",
    "Camera dei Deputati",
    "Euronews Italian",

    "Rai Sport",
    "Sportitalia Plus",
    "SuperTennis",
    "Sportitalia SOLOCALCIO",
    "BIKE Channel",

    "Radio TV Serie A con RDS",
    "RTL 102.5",
    "Radio 105 TV",
    "R101 TV",
    "Deejay TV",
    "RadioItaliaTV",
    "Radio KISS KISS TV",

    "Rai Radio 2 Visual Radio",
    "Radio24-IlSole24OreTV",
    "RadioFreccia",
    "RDS Social TV",
    "Radio ZETA",
    "Radio Montecarlo TV",
    "Virgin Radio TV",
    "Radio m2o Tv",
    "Radio Norba Tv",

    "Tele Quattro Trieste",
    "Tele Friuli",
    "Tele Pordenone",
    "Ran Friul",
    "Videotelecarnia",
]


def clean_name(name):
    """
    Normalizza il nome del canale in modo da confrontare
    correttamente i nomi provenienti dalla sorgente.
    """

    for symbol in "ⒼⓈⓎⓉ":
        name = name.replace(symbol, "")

    return " ".join(name.split()).strip().lower()


def download():
    """
    Scarica la playlist italiana aggiornata di Free-TV.
    """

    request = urllib.request.Request(
        SOURCE,
        headers={
            "User-Agent": "IPTV-Grado/2.2"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=45,
    ) as response:

        return response.read().decode(
            "utf-8-sig",
            errors="replace",
        )


def parse(text):
    """
    Analizza la playlist M3U.

    Per ogni canale restituisce:
    nome
    EXTINF
    eventuali righe aggiuntive
    URL dello stream
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

            if current.startswith(
                ("http://", "https://")
            ):

                url = current

                i += 1

                break

            if current:
                extras.append(current)

            i += 1

        if url:

            channels.append(
                (
                    name,
                    info,
                    extras,
                    url,
                )
            )

    return channels


def stream_score(url):
    """
    Decide quale stream preferire quando Free-TV
    contiene più URL dello stesso canale.

    IMPORTANTE PER LA NOSTRA HISENSE:

    Gli stream Rai CloudFront hanno mostrato
    congelamento su SS IPTV.

    Per questo diamo priorità molto alta ai
    relinker ufficiali Mediapolis Rai.
    """

    lower = url.lower()

    score = 0

    # PRIORITA' MASSIMA RAI
    if "mediapolis.rai.it/relinker" in lower:
        score += 100

    # Preferiamo normali playlist HLS.
    if ".m3u8" in lower:
        score += 10

    # CloudFront resta possibile ma con priorità bassa.
    if "cloudfront.net" in lower:
        score += 5

    return score


# =========================================================
# DOWNLOAD E ANALISI DELLA SORGENTE
# =========================================================

print("Scaricamento playlist Free-TV...")

text = download()

source_channels = parse(text)

print(
    f"Canali/stream letti dalla sorgente: "
    f"{len(source_channels)}"
)


wanted = {
    clean_name(channel): channel
    for channel in WANTED
}


# =========================================================
# RACCOLTA STREAM DISPONIBILI
# =========================================================

candidates = {}


for name, info, extras, url in source_channels:

    normalized = clean_name(name)

    if normalized not in wanted:
        continue

    # Blocca gli stream che sappiamo essere
    # incompatibili con la nostra Hisense.
    if any(
        domain in url
        for domain in BLOCKED
    ):

        print(
            "BLOCCATO:",
            name,
            url,
        )

        continue

    candidates.setdefault(
        normalized,
        [],
    ).append(
        (
            name,
            info,
            extras,
            url,
        )
    )


# =========================================================
# COSTRUZIONE PLAYLIST IPTV GRADO
# =========================================================

output = [
    "#EXTM3U",
    "#PLAYLIST:IPTV Grado - Safe Auto Update v2.2",
    "#NOTA:Ottimizzata per Hisense VIDAA / SS IPTV",
]


added = set()

count = 0


# Mantiene esattamente l'ordine della nostra lista WANTED.
for requested_name in WANTED:

    normalized = clean_name(
        requested_name
    )

    available = candidates.get(
        normalized,
        [],
    )

    if not available:

        print(
            "NON TROVATO:",
            requested_name,
        )

        continue


    # Se Free-TV propone più stream dello stesso canale,
    # scegliamo quello con il punteggio migliore.
    best = max(
        available,
        key=lambda channel:
            stream_score(channel[3]),
    )


    name, info, extras, url = best


    # Sicurezza contro eventuali duplicati.
    if normalized in added:
        continue


    added.add(normalized)


    # =====================================================
    # TELEQUATTRO
    # =====================================================

    # Deve comparire nella nostra playlist come canale 10.
    if normalized == clean_name(
        "Tele Quattro Trieste"
    ):

        info = (
            info.rsplit(",", 1)[0]
            + ",10 - Telequattro"
        )


    output.append(info)

    output.extend(extras)

    output.append(url)


    count += 1


    print(
        "AGGIUNTO:",
        requested_name,
        url,
    )


# =========================================================
# CONTROLLO DI SICUREZZA
# =========================================================

# Se Free-TV dovesse cambiare struttura o diventare
# temporaneamente irraggiungibile, NON vogliamo
# distruggere la playlist che già funziona.

if count < 35:

    raise RuntimeError(
        f"Trovati soltanto {count} canali. "
        "Aggiornamento annullato. "
        "La playlist precedente viene preservata."
    )


# =========================================================
# SALVATAGGIO
# =========================================================

OUTPUT.write_text(
    "\n".join(output) + "\n",
    encoding="utf-8",
)


print("")
print(
    "======================================"
)

print(
    f"IPTV Grado aggiornata: "
    f"{count} canali."
)

print(
    "Duplicati eliminati."
)

print(
    "Rai: priorità Mediapolis."
)

print(
    "Stream Mediaset incompatibili esclusi."
)

print(
    "Telequattro configurato come canale 10."
)

print(
    "======================================"
)
