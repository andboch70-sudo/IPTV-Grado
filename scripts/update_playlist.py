import urllib.request
from pathlib import Path
import re


# =========================================================
# IPTV GRADO - SAFE AUTO UPDATE
# Versione 2.9
# MEDIASET DASH + RADIO MEDIASET DASH + EPG ESTESO
# Hisense VIDAA / SS IPTV
# =========================================================

SOURCE = (
    "https://raw.githubusercontent.com/"
    "Free-TV/IPTV/master/playlists/playlist_italy.m3u8"
)

OUTPUT = Path(
    "IPTV_Grado_Full_v1.0.m3u"
)

EPG_URL = (
    "https://raw.githubusercontent.com/"
    "andboch70-sudo/IPTV-Grado/"
    "refs/heads/main/EPG_Grado.xml"
)


# =========================================================
# MEDIASET DASH
#
# Tutti verificati funzionanti su
# Hisense VIDAA / SS IPTV
# =========================================================

MEDIASET_DASH = {

    "Rete 4":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-r4/r4-clr.isml/manifest.mpd",

    "Canale 5":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-c5/c5-clr.isml/manifest.mpd",

    "Italia 1":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-i1/i1-clr.isml/manifest.mpd",

    "20 Mediaset":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-lb/lb-clr.isml/manifest.mpd",

    "Iris":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-ki/ki-clr.isml/manifest.mpd",

    "TwentySeven":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-ts/ts-clr.isml/manifest.mpd",

    "La5":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-ka/ka-clr.isml/manifest.mpd",

    "Cine34":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-b6/b6-clr.isml/manifest.mpd",

    "Focus":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-fu/fu-clr.isml/manifest.mpd",

    "Top Crime":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-lt/lt-clr.isml/manifest.mpd",

    "Boing":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-kb/kb-clr.isml/manifest.mpd",

    "Italia 2":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-i2/i2-clr.isml/manifest.mpd",

    "Mediaset Extra":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-kq/kq-clr.isml/manifest.mpd",

    "TGCOM24":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-kf/kf-clr.isml/manifest.mpd",

    "Cartoonito":
        "https://live03-col.msf.cdn.mediaset.net/"
        "live/ch-la/la-clr.isml/manifest.mpd",
}


# =========================================================
# RADIO MEDIASET DASH
#
# Verificati direttamente su Hisense VIDAA / SS IPTV.
# Sostituiscono gli HLS live02-seg che causavano freeze.
# =========================================================

RADIO_MEDIASET_DASH = {

    "Radio Montecarlo TV":
        "https://live03-col.msr.cdn.mediaset.net/"
        "live/ch-bb/bb-clr.isml/manifest.mpd",

    "Radio 105 TV":
        "https://live03-col.msr.cdn.mediaset.net/"
        "live/ch-ec/ec-clr.isml/manifest.mpd",

    "R101 TV":
        "https://live03-col.msr.cdn.mediaset.net/"
        "live/ch-er/er-clr.isml/manifest.mpd",

    "Virgin Radio TV":
        "https://live03-col.msr.cdn.mediaset.net/"
        "live/ch-ew/ew-clr.isml/manifest.mpd",
}


# =========================================================
# TV 12 FVG
#
# Verificato direttamente su Hisense VIDAA / SS IPTV.
# Sostituisce Tele Pordenone.
# =========================================================

TV12_URL = (
    "https://59d7d6f47d7fc.streamlock.net/"
    "tv12/tv12/playlist.m3u8"
)


# =========================================================
# EPG IDs
# =========================================================

EPG_IDS = {

    # RAI
    "Rai 1": "Rai1.it",
    "Rai 2": "Rai2.it",
    "Rai 3": "Rai3.it",
    "Rai 4": "Rai4.it",
    "Rai 5": "Rai5.it",
    "Rai Movie": "RaiMovie.it",
    "Rai Premium": "RaiPremium.it",
    "Rai Gulp": "RaiGulp.it",
    "Rai YoYo": "RaiYoyo.it",
    "Rai News 24": "RaiNews24.it",
    "Rai Storia": "RaiStoria.it",
    "Rai Scuola": "RaiScuola.it",
    "Rai Sport": "RaiSport.it",

    # MEDIASET
    "Rete 4": "Rete.4.it",
    "Canale 5": "Canale.5.it",
    "Italia 1": "Italia.1.it",
    "20 Mediaset": "20.it",
    "Iris": "Iris.it",
    "TwentySeven": "27.Twentyseven.it",
    "La5": "La.5.it",
    "Cine34": "Cine34.it",
    "Focus": "Focus.it",
    "Top Crime": "Top.Crime.it",
    "Boing": "Boing.it",
    "Italia 2": "Italia.2.it",
    "Mediaset Extra": "Mediaset.Extra.it",
    "TGCOM24": "TGCom.it",
    "Cartoonito": "Cartoonito.it",

    # ALTRI
    "Nove": "Nove.it",
    "Cielo": "cielo.it",
    "Real Time": "Real.Time.it",
    "Food Network": "Food.Network.it",
    "Discovery Channel": "Discovery.Channel.it",
    "DMAX": "DMAX.it",
    "HGTV": "HGTV.it",
    "K2": "K2.it",
    "Frisbee": "Frisbee.it",
    "Super!": "Super!.it",
    "Sky TG24": "Sky.TG24.it",
    "R101 TV": "R101tv.it",
    "Deejay TV": "Deejay.TV.it",

    # EPG ESTESO
    "La7": "LA7.HD.it",
    "TV8": "TV8.HD.it",
    "Giallo": "Giallo.TV.it",
    "Gambero Rosso": "Gambero.Rosso.HD.it",
    "Euronews Italian": "Euronews.it",
    "SuperTennis": "SuperTennis.HD.it",
    "Sportitalia SOLOCALCIO": "Solocalcio.it.it",
    "BIKE Channel": "BIKE.it",
    "RTL 102.5": "RTL.102.5.HD.it",
    "Radio 105 TV": "Radio.105.it",
    "RadioItaliaTV": "Radio.Italia.TV.HD.it",
    "Rai Radio 2 Visual Radio": "RaiRadio2.it",
    "RadioFreccia": "RADIOFRECCIA.HD.it",
    "Radio Montecarlo TV": "RMC.it",
    "Virgin Radio TV": "Virgin.Radio.it",
    "Radio Norba Tv": "RADIONORBA.TV.it",
}


# =========================================================
# BLOCCO STREAM INCOMPATIBILI
# =========================================================

BLOCKED = (
    "live02-seg.msf.cdn.mediaset.net",
    "live2-mediaset-it.akamaized.net",
    "live3-mediaset-it.akamaized.net",
    "live02-seg.msr.cdn.mediaset.net",
)


# =========================================================
# CANALI
# =========================================================

WANTED = [

    "Rai 1",
    "Rai 2",
    "Rai 3",

    # MEDIASET
    "Rete 4",
    "Canale 5",
    "Italia 1",
    "20 Mediaset",
    "Iris",
    "TwentySeven",
    "La5",
    "Cine34",
    "Focus",
    "Top Crime",
    "Boing",
    "Italia 2",
    "Mediaset Extra",
    "TGCOM24",
    "Cartoonito",

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

    # FVG
    "Tele Quattro Trieste",
    "Tele Friuli",
    "TV 12 FVG",
    "Ran Friul",
    "Videotelecarnia",
]


# =========================================================
# FUNZIONI
# =========================================================

def clean_name(name):

    for symbol in "ⒼⓈⓎⓉ":
        name = name.replace(symbol, "")

    return " ".join(
        name.split()
    ).strip().lower()


def download():

    request = urllib.request.Request(
        SOURCE,
        headers={
            "User-Agent": "IPTV-Grado/2.9"
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

        name = info.split(
            ",",
            1
        )[-1].strip()

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

    # Preserviamo Rai Mediapolis
    if "mediapolis.rai.it/relinker" in lower:
        score += 100

    if ".m3u8" in lower:
        score += 10

    if "cloudfront.net" in lower:
        score += 5

    return score


def build_info(name):

    epg_id = EPG_IDS.get(name)

    if epg_id:

        return (
            '#EXTINF:-1 '
            f'tvg-id="{epg_id}",'
            f'{name}'
        )

    return (
        "#EXTINF:-1,"
        + name
    )


def add_epg_id(
    info,
    requested_name,
):

    epg_id = EPG_IDS.get(
        requested_name
    )

    if not epg_id:
        return info

    parts = info.split(
        ",",
        1
    )

    attributes = parts[0]

    display_name = (
        parts[1]
        if len(parts) > 1
        else requested_name
    )

    attributes = re.sub(
        r'\s+tvg-id="[^"]*"',
        "",
        attributes,
    )

    attributes += (
        f' tvg-id="{epg_id}"'
    )

    return (
        attributes
        + ","
        + display_name
    )


# =========================================================
# DOWNLOAD SORGENTE
# =========================================================

print("")
print("======================================")
print("IPTV GRADO v2.9")
print("DASH STABILE + EPG ESTESO + TV 12 FVG")
print("======================================")
print("")

print(
    "Scaricamento playlist Free-TV..."
)

text = download()

source_channels = parse(text)

print(
    "Canali/stream letti dalla sorgente:",
    len(source_channels)
)


wanted = {
    clean_name(channel): channel
    for channel in WANTED
}

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
# HEADER
# =========================================================

output = [

    (
        '#EXTM3U '
        f'x-tvg-url="{EPG_URL}"'
    ),

    (
        "#PLAYLIST:IPTV Grado - "
        "Stable v2.9 + DASH + EPG esteso + TV 12 FVG"
    ),

    (
        "#NOTA:Ottimizzata per "
        "Hisense VIDAA / SS IPTV"
    ),
]


added = set()

count = 0
epg_count = 0
mediaset_count = 0
radio_mediaset_count = 0


# =========================================================
# GENERAZIONE
# =========================================================

for requested_name in WANTED:

    normalized = clean_name(
        requested_name
    )


    # -----------------------------------------------------
    # MEDIASET TV DASH
    # -----------------------------------------------------

    if requested_name in MEDIASET_DASH:

        url = MEDIASET_DASH[
            requested_name
        ]

        info = build_info(
            requested_name
        )

        output.append(info)
        output.append(url)

        added.add(normalized)

        count += 1
        mediaset_count += 1
        epg_count += 1

        print(
            "MEDIASET DASH + EPG:",
            requested_name,
            EPG_IDS[requested_name],
            url,
        )

        continue


    # -----------------------------------------------------
    # RADIO MEDIASET DASH
    # -----------------------------------------------------

    if requested_name in RADIO_MEDIASET_DASH:

        url = RADIO_MEDIASET_DASH[
            requested_name
        ]

        info = build_info(
            requested_name
        )

        output.append(info)
        output.append(url)

        added.add(normalized)

        count += 1
        radio_mediaset_count += 1

        if requested_name in EPG_IDS:
            epg_count += 1

        print(
            "RADIO MEDIASET DASH:",
            requested_name,
            url,
        )

        continue


    # -----------------------------------------------------
    # TV 12 FVG
    # -----------------------------------------------------

    if requested_name == "TV 12 FVG":

        info = (
            "#EXTINF:-1 "
            'group-title="FVG",'
            "TV 12 FVG"
        )

        output.append(info)
        output.append(TV12_URL)

        added.add(normalized)

        count += 1

        print(
            "TV 12 FVG:",
            TV12_URL,
        )

        continue


    # -----------------------------------------------------
    # ALTRI CANALI
    # -----------------------------------------------------

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


    # TELEQUATTRO = 10

    if normalized == clean_name(
        "Tele Quattro Trieste"
    ):

        info = (
            info.rsplit(",", 1)[0]
            + ",10 - Telequattro"
        )


    # EPG

    info = add_epg_id(
        info,
        requested_name,
    )

    if requested_name in EPG_IDS:

        epg_count += 1

        print(
            "EPG ASSOCIATO:",
            requested_name,
            EPG_IDS[requested_name],
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
# CONTROLLI DI SICUREZZA
# =========================================================

if count < 49:

    raise RuntimeError(
        f"Trovati soltanto {count} canali. "
        "Aggiornamento annullato. "
        "La playlist precedente viene preservata."
    )


if mediaset_count != 15:

    raise RuntimeError(
        "Errore: non sono stati inseriti "
        "tutti i 15 Mediaset DASH."
    )


if radio_mediaset_count != 4:

    raise RuntimeError(
        "Errore: non sono stati inseriti "
        "tutti i 4 RadioMediaset DASH."
    )


# =========================================================
# SCRITTURA
# =========================================================

OUTPUT.write_text(
    "\n".join(output) + "\n",
    encoding="utf-8",
)


# =========================================================
# RISULTATO
# =========================================================

print("")
print("======================================")

print(
    "IPTV Grado aggiornata:",
    count,
    "canali."
)

print(
    "Mediaset TV DASH inseriti:",
    mediaset_count,
)

print(
    "RadioMediaset DASH inseriti:",
    radio_mediaset_count,
)

print(
    "Canali complessivi associati EPG:",
    epg_count,
)

print(
    "Rai: priorita Mediapolis."
)

print(
    "Mediaset TV: DASH live03-col msf."
)

print(
    "RadioMediaset: DASH live03-col msr."
)

print(
    "Telequattro configurato come canale 10."
)

print(
    "Tele Pordenone rimosso."
)

print(
    "TV 12 FVG inserito."
)

print(
    "EPG Grado integrato ed esteso."
)

print(
    "Versione 2.9."
)

print("======================================")
