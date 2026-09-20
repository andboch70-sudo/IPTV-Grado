import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import gzip


# =========================================================
# IPTV GRADO - EPG AUTO UPDATE
# Versione 1.4 - EPG ESTESO
# =========================================================

SOURCE = (
    "https://epgshare01.online/epgshare01/"
    "epg_ripper_IT1.xml.gz"
)

OUTPUT = Path("EPG_Grado.xml")


# =========================================================
# ID EPG VERIFICATI
# =========================================================

WANTED_IDS = {

    # RAI
    "Rai1.it",
    "Rai2.it",
    "Rai3.it",
    "Rai4.it",
    "Rai5.it",
    "RaiMovie.it",
    "RaiPremium.it",
    "RaiGulp.it",
    "RaiYoyo.it",
    "RaiStoria.it",
    "RaiScuola.it",
    "RaiNews24.it",
    "RaiSport.it",

    # MEDIASET - 15 CANALI
    "Rete.4.it",
    "Canale.5.it",
    "Italia.1.it",
    "20.it",
    "Iris.it",
    "27.Twentyseven.it",
    "La.5.it",
    "Cine34.it",
    "Focus.it",
    "Top.Crime.it",
    "Boing.it",
    "Italia.2.it",
    "Mediaset.Extra.it",
    "TGCom.it",
    "Cartoonito.it",

    # ALTRI - GIA PRESENTI
    "cielo.it",
    "Sky.TG24.it",
    "Deejay.TV.it",
    "R101tv.it",
    "Nove.it",
    "DMAX.it",
    "Real.Time.it",
    "HGTV.it",
    "Food.Network.it",
    "Discovery.Channel.it",
    "K2.it",
    "Frisbee.it",
    "Super!.it",

    # NUOVI EPG - v1.4
    "LA7.HD.it",
    "TV8.HD.it",
    "Giallo.TV.it",
    "Gambero.Rosso.HD.it",
    "Euronews.it",
    "SuperTennis.HD.it",
    "Solocalcio.it.it",
    "BIKE.it",
    "RTL.102.5.HD.it",
    "Radio.105.it",
    "Radio.Italia.TV.HD.it",
    "RaiRadio2.it",
    "RADIOFRECCIA.HD.it",
    "RMC.it",
    "Virgin.Radio.it",
    "RADIONORBA.TV.it",
}


print("")
print("======================================")
print("IPTV GRADO - EPG v1.4")
print("EPG ESTESO")
print("======================================")
print("")

print("Scaricamento EPG Italia...")

request = urllib.request.Request(
    SOURCE,
    headers={
        "User-Agent": "IPTV-Grado-EPG/1.4"
    },
)

with urllib.request.urlopen(
    request,
    timeout=90,
) as response:
    compressed = response.read()

xml_data = gzip.decompress(compressed)

print(
    "EPG scaricato:",
    round(len(xml_data) / 1024 / 1024, 2),
    "MB"
)

root = ET.fromstring(xml_data)

selected_ids = set()


# =========================================================
# SELEZIONE CANALI
# =========================================================

print("")
print("Ricerca canali EPG...")
print("")

for channel in root.findall("channel"):

    channel_id = channel.get("id", "")

    names = [
        x.text or ""
        for x in channel.findall("display-name")
    ]

    if channel_id in WANTED_IDS:

        selected_ids.add(channel_id)

        print(
            "EPG TROVATO:",
            channel_id,
            "->",
            names[0] if names else "",
        )


# =========================================================
# CONTROLLO ID MANCANTI
# =========================================================

missing = WANTED_IDS - selected_ids

if missing:

    print("")
    print("ATTENZIONE - ID EPG NON TROVATI:")

    for channel_id in sorted(missing):
        print(
            "NON TROVATO:",
            channel_id
        )


print("")
print(
    "Canali EPG selezionati:",
    len(selected_ids)
)


# =========================================================
# CONTROLLI DI SICUREZZA
#
# Eseguiti PRIMA di sovrascrivere EPG_Grado.xml.
# =========================================================

if len(selected_ids) < 50:

    raise RuntimeError(
        "Troppi pochi canali EPG trovati. "
        "Aggiornamento annullato."
    )


mediaset_ids = {
    "Rete.4.it",
    "Canale.5.it",
    "Italia.1.it",
    "20.it",
    "Iris.it",
    "27.Twentyseven.it",
    "La.5.it",
    "Cine34.it",
    "Focus.it",
    "Top.Crime.it",
    "Boing.it",
    "Italia.2.it",
    "Mediaset.Extra.it",
    "TGCom.it",
    "Cartoonito.it",
}

missing_mediaset = (
    mediaset_ids
    - selected_ids
)

if missing_mediaset:

    raise RuntimeError(
        "Mancano uno o più EPG Mediaset: "
        + ", ".join(
            sorted(missing_mediaset)
        )
    )


# =========================================================
# CREAZIONE EPG RIDOTTO
# =========================================================

new_root = ET.Element("tv")

for channel in root.findall("channel"):

    if channel.get("id") in selected_ids:
        new_root.append(channel)


programme_count = 0

for programme in root.findall("programme"):

    if programme.get("channel") in selected_ids:

        new_root.append(programme)
        programme_count += 1


# =========================================================
# SCRITTURA
# =========================================================

tree = ET.ElementTree(new_root)

ET.indent(
    tree,
    space="  ",
)

tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True,
)

size_mb = (
    OUTPUT.stat().st_size
    / 1024
    / 1024
)


# =========================================================
# RISULTATO
# =========================================================

print("")
print("======================================")
print("EPG GRADO GENERATO")
print("======================================")

print(
    "Canali:",
    len(selected_ids)
)

print(
    "Programmi:",
    programme_count
)

print(
    "Dimensione:",
    round(size_mb, 2),
    "MB"
)

print(
    "Mediaset EPG previsti: 15"
)

print(
    "Nuovi ID EPG v1.4 previsti: 16"
)

print("======================================")
print("")
