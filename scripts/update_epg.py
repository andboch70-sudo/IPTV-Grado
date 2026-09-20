import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import gzip


# =========================================================
# IPTV GRADO - EPG AUTO UPDATE
# Versione 1.1 - MEDIASET
# =========================================================


SOURCE = (
    "https://epgshare01.online/epgshare01/"
    "epg_ripper_IT1.xml.gz"
)

OUTPUT = Path("EPG_Grado.xml")


# =========================================================
# CANALI DA INSERIRE NELL'EPG GRADO
# =========================================================

WANTED = [

    # RAI
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

    # GENERALISTI
    "La7",
    "TV8",
    "Nove",

    # RAI TEMATICI
    "Rai 4",
    "Rai 5",
    "Rai Movie",
    "Rai Premium",

    # INTRATTENIMENTO
    "Cielo",
    "TV2000",
    "Real Time",
    "Food Network",
    "Discovery Channel",
    "Giallo",
    "DMAX",
    "HGTV",

    # BAMBINI
    "K2",
    "Rai Gulp",
    "Rai YoYo",
    "Frisbee",
    "Super!",

    # NEWS / CULTURA
    "Rai News 24",
    "Sky TG24",
    "Rai Storia",
    "Rai Scuola",

    # SPORT
    "Rai Sport",
    "SuperTennis",

    # RADIO TV
    "RTL 102.5",
    "Radio 105 TV",
    "R101 TV",
    "Deejay TV",
    "RadioItaliaTV",
    "Radio Kiss Kiss TV",
]


# =========================================================
# NORMALIZZAZIONE NOMI
# =========================================================

def normalize(text):

    return (
        text.lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .replace(".", "")
    )


# =========================================================
# DOWNLOAD EPG
# =========================================================

print("")
print("======================================")
print("IPTV GRADO - AGGIORNAMENTO EPG")
print("======================================")
print("")

print("Scaricamento EPG Italia...")


request = urllib.request.Request(
    SOURCE,
    headers={
        "User-Agent": "IPTV-Grado-EPG/1.1"
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
    round(
        len(xml_data) / 1024 / 1024,
        2
    ),
    "MB"
)


# =========================================================
# LETTURA XML
# =========================================================

root = ET.fromstring(xml_data)


wanted_normalized = {
    normalize(name)
    for name in WANTED
}


selected_ids = set()


# =========================================================
# RICERCA CANALI
# =========================================================

print("")
print("Ricerca canali EPG...")
print("")


for channel in root.findall("channel"):

    channel_id = channel.get(
        "id",
        ""
    )

    names = [
        x.text or ""
        for x in channel.findall(
            "display-name"
        )
    ]

    matches = False

    for name in names:

        n = normalize(name)

        if n in wanted_normalized:

            matches = True
            break

    if matches:

        selected_ids.add(
            channel_id
        )

        print(
            "EPG TROVATO:",
            channel_id,
            "->",
            names[0] if names else "",
        )


print("")
print(
    "Canali EPG selezionati:",
    len(selected_ids)
)


# =========================================================
# CREAZIONE EPG RIDOTTO
# =========================================================

new_root = ET.Element("tv")


# CANALI

for channel in root.findall("channel"):

    if (
        channel.get("id")
        in selected_ids
    ):

        new_root.append(
            channel
        )


# PROGRAMMI

programme_count = 0


for programme in root.findall(
    "programme"
):

    if (
        programme.get("channel")
        in selected_ids
    ):

        new_root.append(
            programme
        )

        programme_count += 1


# =========================================================
# SCRITTURA FILE
# =========================================================

tree = ET.ElementTree(
    new_root
)


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

print("======================================")
print("")


# =========================================================
# CONTROLLO SICUREZZA
# =========================================================

if len(selected_ids) < 10:

    raise RuntimeError(
        "Troppi pochi canali EPG trovati. "
        "Aggiornamento annullato."
    )
