import urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
OUTPUT = Path("IPTV_Grado_Full_v1.0.m3u")

# Gli stream di questo dominio congelano SS IPTV sul nostro Hisense/VIDAA.
BLOCKED = ("live02-seg.msf.cdn.mediaset.net",)

# Canali che vogliamo mantenere nella playlist.
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
    "Radio Norba Tv", "Tele Quattro Trieste", "Tele Friuli",
    "Tele Pordenone", "Ran Friul", "Videotelecarnia"
]

def download():
    req = urllib.request.Request(
        SOURCE, headers={"User-Agent": "IPTV-Grado/2.0"}
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8-sig", errors="replace")

def parse(text):
    lines = text.splitlines()
    result = []
    i = 0

    while i < len(lines):
        if not lines[i].startswith("#EXTINF"):
            i += 1
            continue

        info = lines[i]
        name = info.split(",", 1)[-1].strip()
        i += 1

        extras = []
        url = None

        while i < len(lines) and not lines[i].startswith("#EXTINF"):
            line = lines[i].strip()
            if line.startswith(("http://", "https://")):
                url = line
                i += 1
                break
            if line:
                extras.append(line)
            i += 1

        if url:
            result.append((name, info, extras, url))

    return result

def clean_name(name):
    for symbol in "ⒼⓈⓎⓉ":
        name = name.replace(symbol, "")
    return " ".join(name.split()).lower()

source = parse(download())
wanted = {clean_name(x) for x in WANTED}

output = [
    "#EXTM3U",
    "#PLAYLIST:IPTV Grado - Safe Auto Update",
    "#NOTA:Aggiornamento automatico con protezione stream incompatibili"
]

count = 0

for name, info, extras, url in source:
    if clean_name(name) not in wanted:
        continue

    if any(domain in url for domain in BLOCKED):
        print("BLOCCATO:", name, url)
        continue

    # Telequattro sempre visualizzato come canale 10.
    if clean_name(name) == clean_name("Tele Quattro Trieste"):
        info = info.rsplit(",", 1)[0] + ",10 - Telequattro"

    output.append(info)
    output.extend(extras)
    output.append(url)
    count += 1

# Sicurezza: non sostituire la playlist se la sorgente è anomala.
if count < 35:
    raise RuntimeError(
        f"Trovati soltanto {count} canali: playlist precedente preservata."
    )

OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"IPTV Grado aggiornata: {count} canali.")
