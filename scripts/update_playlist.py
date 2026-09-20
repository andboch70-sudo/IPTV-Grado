import urllib.request
from pathlib import Path

SOURCE = (
    "https://raw.githubusercontent.com/"
    "Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
)

OUTPUT = Path("IPTV_Grado_Full_v1.0.m3u")


# =========================================================
# IPTV GRADO - SAFE AUTO UPDATE
# Versione 2.4 STABILE - Hisense VIDAA / SS IPTV
# =========================================================


# Stream Mediaset esclusi:
# sulla nostra Hisense / SS IPTV hanno dato
# congelamento oppure schermo nero.
BLOCKED = (
    "live02-seg.msf.cdn.mediaset.net",
    "live2-mediaset-it.akamaized.net",
    "live3-mediaset-it.akamaized.net",
)


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

    for symbol in "ⒼⓈⓎⓉ":
        name = name.replace(symbol, "")

    return " ".join(name.split()).strip().lower()


def download():

    request = urllib.request.Request(
        SOURCE,
        headers={
            "User-Agent": "IPTV-Grado/2.4"
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

    lower = url.lower()

    score = 0

    # Rai:
    # Mediapolis è stato verificato direttamente
    # sulla nostra Hisense ed è stabile.
    if "mediapolis.rai.it/relinker" in lower:
        score += 100

    if ".m3u8" in lower:
        score += 10

    # CloudFront resta seconda scelta.
    if "cloudfront.net" in lower:
        score += 5

    return score


# =========================================================
# DOWNLOAD SORGENTE
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
# RACCOLTA STREAM
# =========================================================

candidates = {}


for name, info, extras, url in source_channels:

    normalized = clean_name(name)

    if normalized not in wanted:
        continue

    if any(
        domain in url.lower()
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
    "#PLAYLIST:IPTV Grado - Stable v2.4",
    "#NOTA:Ottimizzata per Hisense VIDAA / SS IPTV",
]


added = set()

count = 0


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


    best = max(
        available,
        key=lambda channel:
            stream_score(channel[3]),
    )


    name, info, extras, url = best


    if normalized in added:
        continue


    added.add(normalized)


    # =====================================================
    # TELEQUATTRO
    # =====================================================

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
print("======================================")

print(
    f"IPTV Grado aggiornata: "
    f"{count} canali."
)

print("Duplicati eliminati.")

print("Rai: priorita Mediapolis.")

print("Mediaset incompatibili esclusi.")

print("Telequattro configurato come canale 10.")

print("Versione stabile 2.4.")

print("======================================")
